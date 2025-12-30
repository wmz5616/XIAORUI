from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import shutil, os, json
from datetime import datetime
from collections import Counter

from ..models import SessionLocal, KnowledgeNode, KnowledgeEdge, LearningRecord, User, Course, CourseResource, Notification, Question, StudentAnswer, ForumPost
from .auth import get_current_user
from ..services.doubao_ai import ai_agent

router = APIRouter(prefix="/teacher", tags=["Teacher End"])

def get_db():
    db = SessionLocal(); yield db; db.close()

class CourseCreate(BaseModel):
    title: str; description: str
class NodeCreate(BaseModel):
    course_id: int; label: str; weight: float = 1.0
class EdgeCreate(BaseModel):
    source_id: int; target_id: int; relation: str = "前置"
class RemindRequest(BaseModel):
    student_id: int; message: str
class QuestionCreate(BaseModel):
    course_id: int
    content: str
    type: str
    options: List[str] = []
    correct_answer: str
class GradeRequest(BaseModel):
    submission_id: int
    score: int
    comment: str

@router.get("/class-monitor")
def get_class_monitor(db: Session = Depends(get_db)):
    records = db.query(LearningRecord).all()
    students = db.query(User).filter(User.role == 'student').all()
    student_map = {s.id: {"name": s.full_name or s.username, "progress": 0, "weak_count": 0, "is_silenced": s.is_silenced} for s in students}
    
    for r in records:
        if r.student_id in student_map:
            if r.mastery_level >= 0.8: student_map[r.student_id]["progress"] += 5
            elif r.mastery_level < 0.6: student_map[r.student_id]["weak_count"] += 1

    result = []
    for sid, data in student_map.items():
        prog = min(100, data["progress"])
        status = "Risk" if (data["weak_count"] > 2 or prog < 30) else "Normal"
        result.append({
            "id": sid, "name": data["name"],
            "weakness": f"累计 {data['weak_count']} 个薄弱点" if data['weak_count'] > 0 else "无",
            "progress": prog, "status": status, "is_silenced": data["is_silenced"]
        })
    return result

@router.post("/generate-report")
def generate_class_report(db: Session = Depends(get_db)):
    return {"report": "AI 报告生成功能（复用之前代码即可）"} 

@router.post("/remind-student")
def remind_student(req: RemindRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_notif = Notification(user_id=req.student_id, content=f"【老师提醒】{req.message}", is_read=False)
    db.add(new_notif); db.commit()
    return {"msg": "发送成功"}

@router.post("/courses")
def create_course(course: CourseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_course = Course(title=course.title, description=course.description, teacher_id=current_user.id, status="published")
    db.add(new_course); db.commit(); db.refresh(new_course)
    return {"msg": "创建成功", "id": new_course.id}

@router.get("/my-courses")
def get_teacher_courses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Course).all()

@router.post("/upload-resource")
async def upload_resource(course_id: int = Form(...), title: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    os.makedirs("uploads", exist_ok=True)
    file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_path = f"uploads/{file_name}"
    with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    new_res = CourseResource(course_id=course_id, title=title, type="video" if "mp4" in file.filename else "document", url=f"http://localhost:8000/{file_path}")
    db.add(new_res); db.commit()
    return {"msg": "上传成功"}

@router.post("/questions")
def create_question(q: QuestionCreate, db: Session = Depends(get_db)):
    options_str = json.dumps(q.options, ensure_ascii=False) if q.type == 'choice' else ""
    new_q = Question(
        course_id=q.course_id, content=q.content, type=q.type,
        options_json=options_str, correct_answer=q.correct_answer
    )
    db.add(new_q); db.commit()
    return {"msg": "题目录入成功"}

@router.get("/submissions/pending")
def get_pending_submissions(db: Session = Depends(get_db)):
    subs = db.query(StudentAnswer).join(Question).filter(
        StudentAnswer.score == None, 
        Question.type == 'text'
    ).all()
    
    result = []
    for s in subs:
        result.append({
            "id": s.id,
            "student_name": s.student.full_name or s.student.username,
            "question_content": s.question.content,
            "answer_content": s.answer_content,
            "submitted_at": s.submitted_at.strftime("%Y-%m-%d %H:%M")
        })
    return result

@router.post("/submissions/grade")
def grade_submission(req: GradeRequest, db: Session = Depends(get_db)):
    sub = db.query(StudentAnswer).filter(StudentAnswer.id == req.submission_id).first()
    if not sub: raise HTTPException(404, "作业不存在")
    
    sub.score = req.score
    sub.teacher_comment = req.comment
    
    notif = Notification(user_id=sub.student_id, content=f"你的作业《{sub.question.content[:10]}...》已被批改，得分：{req.score}", is_read=False)
    db.add(notif)
    db.commit()
    return {"msg": "批改完成"}

@router.get("/forum/posts")
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(ForumPost).order_by(ForumPost.created_at.desc()).all()
    return [{
        "id": p.id, "title": p.title, "author": p.author.full_name, 
        "is_pinned": p.is_pinned, "content": p.content[:50]
    } for p in posts]

@router.delete("/forum/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db.query(ForumPost).filter(ForumPost.id == post_id).delete()
    db.commit()
    return {"msg": "已删除"}

@router.put("/forum/posts/{post_id}/pin")
def toggle_pin(post_id: int, db: Session = Depends(get_db)):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if post: 
        post.is_pinned = not post.is_pinned
        db.commit()
    return {"msg": "操作成功"}

@router.put("/students/{student_id}/silence")
def toggle_silence(student_id: int, db: Session = Depends(get_db)):
    stu = db.query(User).filter(User.id == student_id).first()
    if stu:
        stu.is_silenced = not stu.is_silenced
        db.commit()
        status = "已禁言" if stu.is_silenced else "已解除"
        return {"msg": f"用户{status}"}
    return {"msg": "用户不存在"}

@router.post("/add-node")
def add_node(node: NodeCreate, db: Session = Depends(get_db)):
    new_node = KnowledgeNode(course_id=node.course_id, label=node.label, weight=node.weight)
    db.add(new_node); db.commit(); db.refresh(new_node)
    return {"msg": "添加成功", "node_id": new_node.id}

@router.post("/add-edge")
def add_edge(edge: EdgeCreate, db: Session = Depends(get_db)):
    new_edge = KnowledgeEdge(source_id=edge.source_id, target_id=edge.target_id, relation_type=edge.relation)
    db.add(new_edge); db.commit()
    return {"msg": "关联成功"}

@router.get("/course-nodes/{course_id}")
def get_nodes_list(course_id: int, db: Session = Depends(get_db)):
    nodes = db.query(KnowledgeNode).filter(KnowledgeNode.course_id == course_id).all()
    return [{"id": n.id, "label": n.label} for n in nodes]