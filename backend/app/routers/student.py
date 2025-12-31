from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..models import SessionLocal, Course, User, LearningRecord, CourseResource, Notification, Question, StudentAnswer
from .auth import get_current_user

router = APIRouter(prefix="/student", tags=["Student End"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None

@router.get("/homeworks")
def get_student_homeworks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取学生作业列表：
    列出所有有题目的课程，并显示完成进度。
    """
    courses_with_questions = db.query(Course).join(Question).distinct().all()
    
    homework_list = []
    
    for course in courses_with_questions:
        total_questions = db.query(Question).filter(Question.course_id == course.id).count()

        answered_count = db.query(StudentAnswer).join(Question).filter(
            StudentAnswer.student_id == current_user.id,
            Question.course_id == course.id
        ).count()

        status = "pending"
        if answered_count > 0:
            if answered_count >= total_questions:
                status = "completed"
            else:
                status = "in_progress"

        teacher = db.query(User).filter(User.id == course.teacher_id).first()
        teacher_name = teacher.full_name if teacher else "未知教师"

        homework_list.append({
            "course_id": course.id,
            "course_title": course.title,
            "teacher_name": teacher_name,
            "total_questions": total_questions,
            "answered_questions": answered_count,
            "status": status
        })
        
    return homework_list

@router.get("/courses")
def get_all_courses(db: Session = Depends(get_db)):
    """获取所有已发布的课程"""
    return db.query(Course).filter(Course.status == "published").all()

@router.get("/course/{course_id}/resources")
def get_course_resources(course_id: int, db: Session = Depends(get_db)):
    """获取课程资源"""
    return db.query(CourseResource).filter(CourseResource.course_id == course_id).all()

@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    learn_days = 12
    notes_count = 5 
    
    return {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "learn_time": current_user.learn_time,
        "learn_days": learn_days,
        "notes_count": notes_count,
        "radar_data": [80, 60, 70, 90, 50, 75]
    }

@router.put("/profile")
def update_profile(info: StudentUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if info.full_name:
        user.full_name = info.full_name
    db.commit()
    return {"msg": "更新成功"}

@router.get("/notifications")
def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return [{
        "id": n.id,
        "content": n.content,
        "is_read": n.is_read,
        "created_at": n.created_at.strftime("%m-%d %H:%M")
    } for n in notifs]

@router.put("/notifications/{notif_id}/read")
def read_notification(notif_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.query(Notification).filter(
        Notification.id == notif_id, 
        Notification.user_id == current_user.id
    ).first()
    
    if n:
        n.is_read = True
        db.commit()
    return {"msg": "已读"}