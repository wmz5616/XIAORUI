from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..models import SessionLocal, Course, User, LearningRecord, CourseResource, Notification, Question, StudentAnswer, Homework
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
    获取学生作业列表（适配新 Homework 模型）：
    1. 遍历所有作业包。
    2. 计算完成状态（未开始/待批改/已完成）。
    3. 显示得分和评语。
    """
    all_homeworks = db.query(Homework).all()
    
    homework_list = []
    
    for hw in all_homeworks:
        course = db.query(Course).filter(Course.id == hw.course_id).first()
        if not course: continue

        questions = hw.questions
        q_ids = [q.id for q in questions]
        total_questions = len(q_ids)
        
        if total_questions == 0: continue

        answers = db.query(StudentAnswer).filter(
            StudentAnswer.student_id == current_user.id,
            StudentAnswer.question_id.in_(q_ids)
        ).all()
        
        answ_count = len(answers)

        status = "pending"
        score_display = None
        comment_display = None
        submitted_time = None

        if answ_count > 0:
            submitted_time = answers[0].submitted_at.strftime("%Y-%m-%d")
            
            has_ungraded = any(a.score is None for a in answers)
            
            if has_ungraded:
                status = "submitted"
            elif answ_count < total_questions:
                status = "in_progress"
            else:
                status = "completed"
                total_score = sum((a.score or 0) for a in answers)
                score_display = total_score

                for a in answers:
                    if a.teacher_comment:
                        comment_display = a.teacher_comment
                        break

        teacher = db.query(User).filter(User.id == course.teacher_id).first()
        teacher_name = teacher.full_name if teacher else "未知教师"

        homework_list.append({
            "homework_id": hw.id,
            "title": hw.title,
            "course_title": course.title,
            "teacher_name": teacher_name,
            "total_questions": total_questions,
            "status": status,
            "score": score_display,
            "comment": comment_display,
            "submitted_at": submitted_time
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
    notes_count = db.query(StudentAnswer).filter(StudentAnswer.student_id == current_user.id).count()
    
    return {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "learn_time": current_user.learn_time,
        "learn_days": learn_days,
        "notes_count": notes_count,
        "radar_data": [85, 70, 75, 90, 60, 80]
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
    """
    获取消息通知：
    老师批改作业后，会写入 Notification 表，这里负责读取。
    """
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