from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import SessionLocal, User, Course, LearningRecord, SystemConfig, CourseResource
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

def get_db():
    db = SessionLocal(); yield db; db.close()

# --- 模型 ---
class SystemStats(BaseModel):
    user_count: int
    course_count: int
    active_students: int

class AiConfig(BaseModel):
    recommendation_threshold: float
    model_version: str

# 1. 获取统计
@router.get("/stats", response_model=SystemStats)
def get_stats(db: Session = Depends(get_db)):
    u_count = db.query(User).count()
    c_count = db.query(Course).count()
    active = db.query(LearningRecord).group_by(LearningRecord.student_id).count()
    return {"user_count": u_count, "course_count": c_count, "active_students": active}

# 2. 获取用户列表
@router.get("/users")
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    db.delete(user); db.commit()
    return {"msg": "已删除"}

# 3. AI 配置
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

# 4. 【新增】资源审核接口
@router.get("/resources")
def get_all_resources(db: Session = Depends(get_db)):
    # 联表查询：资源 -> 课程 -> 老师
    resources = db.query(CourseResource).all()
    result = []
    for r in resources:
        course = db.query(Course).filter(Course.id == r.course_id).first()
        teacher_name = "未知"
        course_title = "未知课程"
        
        if course:
            course_title = course.title
            teacher = db.query(User).filter(User.id == course.teacher_id).first()
            if teacher: teacher_name = teacher.full_name
            
        result.append({
            "id": r.id,
            "title": r.title,
            "type": r.type,
            "url": r.url,
            "course": course_title,
            "teacher": teacher_name,
            "created_at": "刚刚" # 数据库若无时间字段暂略
        })
    return result

@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    res = db.query(CourseResource).filter(CourseResource.id == resource_id).first()
    if not res: raise HTTPException(404, "资源不存在")
    
    # 这里仅删除数据库记录，实际生产环境还应删除磁盘文件
    db.delete(res)
    db.commit()
    return {"msg": "资源已删除"}