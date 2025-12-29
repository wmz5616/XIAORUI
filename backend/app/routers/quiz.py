from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import random

# 引入本地模块
from ..models import SessionLocal, User, LearningRecord, Course
from .auth import get_current_user

router = APIRouter(prefix="/quiz", tags=["Quiz & Assessment"])

def get_db():
    db = SessionLocal(); yield db; db.close()

# --- 模型 ---
class Question(BaseModel):
    id: int
    content: str
    options: List[str] # ["A. xxx", "B. xxx", "C. xxx", "D. xxx"]
    correct_answer: int # 0, 1, 2, 3 (对应索引)

class QuizResult(BaseModel):
    score: int
    passed: bool
    mastery_update: str

# --- 模拟题库数据 (实际应存数据库) ---
# key: course_id
MOCK_QUESTIONS = {
    1: [ # 课程ID 1 的题目
        {"id": 101, "content": "斐波那契数列的第3项是多少？(0, 1, 1, 2...)", "options": ["1", "2", "3", "0"], "correct": 0},
        {"id": 102, "content": "一元二次方程 ax^2+bx+c=0 的判别式是？", "options": ["b^2-4ac", "b^2+4ac", "2a", "sqrt(abc)"], "correct": 0},
        {"id": 103, "content": "函数 y=x^2 的图像是？", "options": ["直线", "双曲线", "抛物线", "圆"], "correct": 2},
    ]
}

# 1. 获取课程测验题
@router.get("/{course_id}", response_model=List[Question])
def get_quiz(course_id: int, db: Session = Depends(get_db)):
    # 模拟：随机返回 3 道题
    questions = MOCK_QUESTIONS.get(course_id, [])
    if not questions:
        # 默认题目
        return [
            {"id": 999, "content": "本课程的基础概念测试：1+1=？", "options": ["2", "3", "4", "1"], "correct_answer": 0}
        ]
    
    # 转换格式
    return [
        Question(id=q["id"], content=q["content"], options=q["options"], correct_answer=q["correct"]) 
        for q in questions
    ]

# 2. 提交答案并更新掌握度
@router.post("/{course_id}/submit", response_model=QuizResult)
def submit_quiz(course_id: int, answers: List[int], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. 自动判分
    questions = MOCK_QUESTIONS.get(course_id, [])
    if not questions: return {"score": 100, "passed": True, "mastery_update": "无需更新"}
    
    correct_count = 0
    for i, q in enumerate(questions):
        if i < len(answers) and answers[i] == q["correct"]:
            correct_count += 1
            
    score = int((correct_count / len(questions)) * 100)
    passed = score >= 60
    
    # 2. 更新学习记录 (核心逻辑：分数驱动图谱)
    # 查找该学生在该课程的学习记录
    record = db.query(LearningRecord).filter(
        LearningRecord.student_id == current_user.id,
        # 简化：这里假设 LearningRecord 关联的是课程，或者我们更新最近的一条记录
    ).first()
    
    msg = "保持现状"
    if passed:
        # 模拟：如果通过，更新知识点掌握度
        msg = "掌握度提升！图谱节点已变绿"
        # 实际项目中这里应更新 KnowledgeNode 的 status
    else:
        msg = "未通过，建议重新学习前置课程"
        
    return {"score": score, "passed": passed, "mastery_update": msg}