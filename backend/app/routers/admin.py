from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import SessionLocal, User, Course, LearningRecord, SystemConfig, CourseResource
from pydantic import BaseModel
from typing import List
import random
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

def get_db():
    db = SessionLocal(); yield db; db.close()
    
class SystemStats(BaseModel):
    user_count: int
    course_count: int
    active_students: int

class AiConfig(BaseModel):
    recommendation_threshold: float
    model_version: str

class RoleUpdate(BaseModel):
    role: str

class SystemStatus(BaseModel):
    cpu_usage: int
    memory_usage: int
    disk_usage: int
    status: str

class LogItem(BaseModel):
    id: int
    level: str
    message: str
    time: str

@router.get("/stats", response_model=SystemStats)
def get_stats(db: Session = Depends(get_db)):
    u_count = db.query(User).count()
    c_count = db.query(Course).count()
    active = db.query(LearningRecord).group_by(LearningRecord.student_id).count()
    return {"user_count": u_count, "course_count": c_count, "active_students": active}

@router.get("/stats/trend")
def get_stats_trend(db: Session = Depends(get_db)):
    dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(6, -1, -1)]
    
    new_users = [random.randint(2, 10) for _ in range(7)]

    daily_active = [random.randint(10, 50) for _ in range(7)]
    
    return {
        "dates": dates,
        "new_users": new_users,
        "daily_active": daily_active
    }

@router.get("/users")
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    if role_data.role not in ['student', 'teacher', 'admin']:
        raise HTTPException(400, "无效的角色类型")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "用户不存在")
    
    user.role = role_data.role
    db.commit()
    return {"msg": f"用户 {user.username} 已变更为 {role_data.role}"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    db.delete(user); db.commit()
    return {"msg": "已删除"}

@router.get("/ai-config")
def get_ai_config(db: Session = Depends(get_db)):
    conf = db.query(SystemConfig).filter_by(key="ai_threshold").first()
    val = float(conf.value) if conf else 0.6
    return {"recommendation_threshold": val, "model_version": "Doubao-Pro-4k"}

@router.post("/ai-config")
def update_ai_config(config: AiConfig, db: Session = Depends(get_db)):
    conf = db.query(SystemConfig).filter_by(key="ai_threshold").first()
    if not conf:
        conf = SystemConfig(key="ai_threshold", value=str(config.recommendation_threshold))
        db.add(conf)
    else:
        conf.value = str(config.recommendation_threshold)
    db.commit()
    return {"msg": "更新成功"}

@router.get("/resources")
def get_all_resources(db: Session = Depends(get_db)):
    resources = db.query(CourseResource).all()
    result = []
    for r in resources:
        course = db.query(Course).filter(Course.id == r.course_id).first()
        teacher_name, course_title = "未知", "未知课程"
        
        if course:
            course_title = course.title
            teacher = db.query(User).filter(User.id == course.teacher_id).first()
            if teacher: teacher_name = teacher.full_name
            
        result.append({
            "id": r.id, "title": r.title, "type": r.type, "url": r.url,
            "course": course_title, "teacher": teacher_name, "created_at": "近期"
        })
    return result

@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    res = db.query(CourseResource).filter(CourseResource.id == resource_id).first()
    if not res: raise HTTPException(404, "资源不存在")
    db.delete(res); db.commit()
    return {"msg": "资源已删除"}

@router.get("/system/status", response_model=SystemStatus)
def get_system_status():
    cpu = random.randint(10, 40)
    mem = random.randint(30, 60)
    disk = 45
    return {
        "cpu_usage": cpu,
        "memory_usage": mem,
        "disk_usage": disk,
        "status": "Healthy" if cpu < 80 else "High Load"
    }

@router.get("/system/logs", response_model=List[LogItem])
def get_system_logs():
    logs = [
        {"id": 1, "level": "INFO", "message": "System backup completed successfully.", "time": "10:00"},
        {"id": 2, "level": "INFO", "message": "User login rate increased by 5%.", "time": "10:15"},
        {"id": 3, "level": "WARN", "message": "High latency detected in API gateway.", "time": "10:30"},
        {"id": 4, "level": "ERROR", "message": "Failed to sync with external CDN.", "time": "10:45"},
        {"id": 5, "level": "INFO", "message": "Scheduled maintenance task started.", "time": "11:00"},
    ]
    return logs