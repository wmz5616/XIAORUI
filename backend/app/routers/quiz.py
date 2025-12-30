from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import json
from datetime import datetime

from ..models import SessionLocal, User, LearningRecord, Course, KnowledgeNode, Question
from .auth import get_current_user

router = APIRouter(prefix="/quiz", tags=["Quiz & Assessment"])

def get_db():
    db = SessionLocal(); yield db; db.close()

# --- 模型 ---
class QuestionModel(BaseModel):
    id: int
    content: str
    options: List[str]
    correct_answer: int

class QuizResult(BaseModel):
    score: int
    passed: bool
    mastery_update: str

# 1. 获取真实题目
@router.get("/{course_id}", response_model=List[QuestionModel])
def get_quiz(course_id: int, db: Session = Depends(get_db)):
    # 从数据库查询该课程的题目
    db_questions = db.query(Question).filter(Question.course_id == course_id).all()
    
    if not db_questions:
        return []
    
    # 格式转换
    result = []
    for q in db_questions:
        try:
            opts = json.loads(q.options_json)
        except:
            opts = ["解析选项失败"]
            
        result.append(QuestionModel(
            id=q.id,
            content=q.content,
            options=opts,
            correct_answer=q.correct_answer
        ))
    return result

# 2. 提交并判分
@router.post("/{course_id}/submit", response_model=QuizResult)
def submit_quiz(course_id: int, answers: List[int], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. 查库获取标准答案
    db_questions = db.query(Question).filter(Question.course_id == course_id).all()
    
    if not db_questions:
        return {"score": 0, "passed": False, "mastery_update": "该课程暂无题目"}
    
    correct_count = 0
    # 简单的按顺序比对 (假设前端提交顺序与 DB 查询顺序一致，实际生产可用 ID 映射)
    for i, q in enumerate(db_questions):
        if i < len(answers) and answers[i] == q.correct_answer:
            correct_count += 1
            
    score = int((correct_count / len(db_questions)) * 100)
    passed = score >= 60
    
    msg = "未通过，请回顾课程内容"
    
    # 2. 通过则更新数据库记录
    if passed:
        msg = "通过！知识点已点亮，学习时长已累积"
        
        # A. 更新知识点掌握度
        course_nodes = db.query(KnowledgeNode).filter(KnowledgeNode.course_id == course_id).all()
        for node in course_nodes:
            record = db.query(LearningRecord).filter(
                LearningRecord.student_id == current_user.id,
                LearningRecord.knowledge_node_id == node.id
            ).first()
            
            if not record:
                record = LearningRecord(
                    student_id=current_user.id, 
                    knowledge_node_id=node.id,
                    mastery_level=1.0,
                    status="mastered"
                )
                db.add(record)
            else:
                record.mastery_level = 1.0
                record.status = "mastered"
                record.last_practice_date = datetime.now()
        
        # B. 累积学习时长 (模拟：每次通过测验增加 30 分钟)
        current_user.learn_time += 30
        db.add(current_user)
        
        db.commit()
        
    return {"score": score, "passed": passed, "mastery_update": msg}