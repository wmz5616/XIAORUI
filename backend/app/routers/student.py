from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ..models import SessionLocal, Course, CourseResource, KnowledgeNode, KnowledgeEdge, User, LearningRecord, Notification
from .auth import get_current_user

router = APIRouter(prefix="/student", tags=["Student Learning"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CourseModel(BaseModel):
    id: int
    title: str
    description: str
    teacher_name: str = "未知教师"
    class Config: from_attributes = True

class ResourceModel(BaseModel):
    id: int; title: str; type: str; url: str

class UserProfile(BaseModel):
    username: str
    full_name: str
    role: str
    learn_time: int      
    finished_courses: int 
    ability_radar: List[int]

class NotificationModel(BaseModel):
    id: int
    content: str
    is_read: bool
    time: str

@router.get("/courses", response_model=List[CourseModel])
def get_all_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.status == "published").all()
    return courses

@router.get("/course/{course_id}/resources", response_model=List[ResourceModel])
def get_course_resources(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return db.query(CourseResource).filter(CourseResource.course_id == course_id).all()

@router.get("/knowledge-graph/{course_id}")
def get_knowledge_graph(
    course_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    nodes = db.query(KnowledgeNode).filter(KnowledgeNode.course_id == course_id).all()
    if not nodes: return {"nodes": [], "links": [], "categories": []}
        
    node_ids = [n.id for n in nodes]
    links = db.query(KnowledgeEdge).filter(
        KnowledgeEdge.source_id.in_(node_ids),
        KnowledgeEdge.target_id.in_(node_ids)
    ).all()

    records = db.query(LearningRecord).filter(LearningRecord.student_id == current_user.id).all()
    mastered_map = {r.knowledge_node_id: (r.mastery_level >= 0.8) for r in records}

    formatted_nodes = [{
        "id": str(n.id),
        "name": n.label,
        "symbolSize": n.weight * 30 + 10, 
        "category": 1 if mastered_map.get(n.id, False) else 0,
        "draggable": True,
        "value": n.weight
    } for n in nodes]

    formatted_links = [{"source": str(l.source_id), "target": str(l.target_id)} for l in links]

    return {
        "nodes": formatted_nodes,
        "links": formatted_links,
        "categories": [{"name": "未掌握", "color": "#F56C6C"}, {"name": "已掌握", "color": "#67C23A"}]
    }

@router.get("/profile", response_model=UserProfile)
def get_student_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mastered_count = db.query(LearningRecord).filter(
        LearningRecord.student_id == current_user.id,
        LearningRecord.mastery_level >= 0.8
    ).count()

    base_score = 40
    dynamic_score = min(100, base_score + (mastered_count * 15))
    radar_data = [dynamic_score, min(100, dynamic_score + 10), min(100, dynamic_score - 5), min(100, dynamic_score + 5), dynamic_score]
    
    real_learn_time = getattr(current_user, 'learn_time', 0)

    return {
        "username": current_user.username,
        "full_name": current_user.full_name or "未命名",
        "role": current_user.role,
        "learn_time": real_learn_time, 
        "finished_courses": int(mastered_count / 3),
        "ability_radar": radar_data
    }

@router.get("/notifications", response_model=List[NotificationModel])
def get_my_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return [{
        "id": n.id,
        "content": n.content,
        "is_read": n.is_read,
        "time": n.created_at.strftime("%Y-%m-%d %H:%M")
    } for n in notifs]

@router.post("/notifications/{notif_id}/read")
def read_notification(notif_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(
        Notification.id == notif_id, 
        Notification.user_id == current_user.id
    ).first()
    
    if notif:
        notif.is_read = True
        db.commit()
    return {"msg": "已读"}