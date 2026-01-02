from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Union, Optional
import json
from datetime import datetime
from ..models import SessionLocal, User, LearningRecord, Course, Question, StudentAnswer, KnowledgeNode, Homework
from .auth import get_current_user

router = APIRouter(prefix="/quiz", tags=["Quiz & Assessment"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class QuestionModel(BaseModel):
    id: int
    content: str
    type: str
    options: List[str]

class SubmitItem(BaseModel):
    question_id: int
    answer: Union[int, str]

class QuizResult(BaseModel):
    auto_score: int
    total_score: int
    msg: str
    requires_review: bool

@router.get("/{homework_id}", response_model=List[QuestionModel])
def get_quiz(homework_id: int, db: Session = Depends(get_db)):
    """
    获取指定作业下的所有题目
    参数改为 homework_id，确保只获取该次作业的题
    """
    hw = db.query(Homework).filter(Homework.id == homework_id).first()
    if not hw:
        raise HTTPException(status_code=404, detail="作业不存在")

    db_questions = db.query(Question).filter(Question.homework_id == homework_id).all()
    
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

@router.post("/{homework_id}/submit", response_model=QuizResult)
def submit_quiz(
    homework_id: int, 
    answers: List[SubmitItem], 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    提交作业逻辑修复：
    1. 动态计算总分（题目数 * 10）。
    2. 修复通过率判断逻辑。
    """
    questions = db.query(Question).filter(Question.homework_id == homework_id).all()
    if not questions:
        raise HTTPException(404, "作业题目数据异常")
        
    total_questions = len(questions)
    max_possible_score = total_questions * 10
    total_auto_score = 0
    has_subjective = False
    valid_q_ids = {q.id: q for q in questions}
    
    for item in answers:
        if item.question_id not in valid_q_ids:
            continue
            
        q = valid_q_ids[item.question_id]
        current_score = 0
        is_graded = False

        if q.type == 'choice':
            is_graded = True
            user_ans = str(item.answer).strip()
            correct_ans = str(q.correct_answer).strip()

            if user_ans == correct_ans:
                current_score = 10
                total_auto_score += current_score
            else:
                current_score = 0

        elif q.type == 'text':
            has_subjective = True
            is_graded = False

        existing_ans = db.query(StudentAnswer).filter(
            StudentAnswer.student_id == current_user.id,
            StudentAnswer.question_id == q.id
        ).first()
        
        score_to_save = current_score if is_graded else None
        
        if existing_ans:
            existing_ans.answer_content = str(item.answer)
            existing_ans.submitted_at = datetime.now()
            existing_ans.score = score_to_save
            if not is_graded:
                existing_ans.teacher_comment = None
        else:
            new_ans = StudentAnswer(
                student_id=current_user.id,
                question_id=q.id,
                answer_content=str(item.answer),
                score=score_to_save,
                submitted_at=datetime.now()
            )
            db.add(new_ans)

    db.commit()
    
    if has_subjective:
        return {
            "auto_score": total_auto_score,
            "total_score": max_possible_score,
            "msg": f"作业已提交！客观题得分 {total_auto_score} 分，主观题请等待老师批改。",
            "requires_review": True
        }
    else:
        pass_ratio = total_auto_score / max_possible_score if max_possible_score > 0 else 0
        pass_status = "通过" if pass_ratio >= 0.6 else "未通过"
        
        return {
            "auto_score": total_auto_score,
            "total_score": max_possible_score,
            "msg": f"作业已完成！得分：{total_auto_score} / {max_possible_score} ({pass_status})",
            "requires_review": False
        }