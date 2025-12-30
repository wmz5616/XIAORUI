from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Union, Optional
import json
from datetime import datetime

from ..models import SessionLocal, User, LearningRecord, Course, Question, StudentAnswer, KnowledgeNode
from .auth import get_current_user

router = APIRouter(prefix="/quiz", tags=["Quiz & Assessment"])

def get_db():
    db = SessionLocal(); yield db; db.close()

class QuestionModel(BaseModel):
    id: int
    content: str
    type: str
    options: List[str]

class SubmitItem(BaseModel):
    question_id: int
    answer: Union[int, str]

class QuizResult(BaseModel):
    score: int
    passed: bool
    mastery_update: str

@router.get("/{course_id}", response_model=List[QuestionModel])
def get_quiz(course_id: int, db: Session = Depends(get_db)):
    db_questions = db.query(Question).filter(Question.course_id == course_id).all()
    
    result = []
    for q in db_questions:
        opts = []
        if q.type == 'choice' and q.options_json:
            try:
                opts = json.loads(q.options_json)
            except:
                opts = []
        
        result.append(QuestionModel(
            id=q.id,
            content=q.content,
            type=q.type,
            options=opts
        ))
    return result

@router.post("/{course_id}/submit", response_model=QuizResult)
def submit_quiz(course_id: int, answers: List[SubmitItem], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    score = 0
    total_choice_questions = 0
    correct_choice_count = 0
    has_text_question = False
    
    for item in answers:
        q = db.query(Question).filter(Question.id == item.question_id).first()
        if not q: continue
        
        if q.type == 'choice':
            total_choice_questions += 1
            if str(item.answer) == str(q.correct_answer):
                correct_choice_count += 1
                
        elif q.type == 'text':
            has_text_question = True
            existing_ans = db.query(StudentAnswer).filter(
                StudentAnswer.student_id == current_user.id,
                StudentAnswer.question_id == q.id
            ).first()
            
            if existing_ans:
                existing_ans.answer_content = str(item.answer)
                existing_ans.submitted_at = datetime.now()
                existing_ans.score = None
            else:
                new_ans = StudentAnswer(
                    student_id=current_user.id,
                    question_id=q.id,
                    answer_content=str(item.answer),
                    score=None
                )
                db.add(new_ans)

    final_score = 0
    if total_choice_questions > 0:
        final_score = int((correct_choice_count / total_choice_questions) * 100)
    
    msg = ""
    passed = False
    if has_text_question:
        msg = f"主观题已提交，请等待老师批改。客观题得分：{final_score}分"
        passed = False 
    else:
        passed = final_score >= 60
        if passed:
            msg = "恭喜通过！知识点掌握状态已更新"
        else:
            msg = "未通过，请继续复习"

    db.commit()
    
    return {"score": final_score, "passed": passed, "mastery_update": msg}