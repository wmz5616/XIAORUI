from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime

from ..models import SessionLocal, KnowledgeNode, KnowledgeEdge, LearningRecord, User
from ..services.doubao_ai import ai_agent
from .auth import get_current_user 

router = APIRouter(prefix="/ai-engine", tags=["AI Core"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class StudentProfile(BaseModel):
    name: str
    grade: str | int 
    weak_subjects: List[str]

class DiagnosticRequest(BaseModel):
    mode: str = "subject"     
    grade: str | int = "高一"  
    subject: str = "数学"
    topic: Optional[str] = None 

class AnalyzeRequest(BaseModel):
    wrong_questions: List[dict] 

@router.post("/diagnostic/start")
def start_diagnostic(req: DiagnosticRequest, current_user: User = Depends(get_current_user)):
    """
    开始诊断：
    前端发送 { mode: 'topic', topic: '三角函数', grade: '高一', subject: '数学' }
    后端根据 mode 决定是按学科出题，还是按知识点出题。
    """
    print(f"用户 {current_user.username} 请求诊断: 模式={req.mode}, 内容={req.topic or req.subject}")
    
    target_content = req.topic if (req.mode == 'topic' and req.topic) else req.subject
    
    try:
        questions = ai_agent.generate_diagnostic_quiz(str(req.grade), target_content)
        return questions
    except Exception as e:
        print(f"AI 出题失败: {e}")
        return [
            {"content": f"【AI服务暂时繁忙】请问 {target_content} 的核心概念是？", "options": ["选项A", "选项B", "选项C", "选项D"], "answer": 0}
        ]

@router.post("/diagnostic/analyze")
def analyze_diagnostic(
    req: AnalyzeRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    分析错题，提取薄弱点，并存入数据库
    """
    if not req.wrong_questions:
        return {"weak_points": []}
        
    try:
        weak_points = ai_agent.analyze_weakness(req.wrong_questions)
    except Exception as e:
        print(f"AI 分析失败: {e}")
        return {"weak_points": ["基础概念掌握不牢", "审题不清"]}

    new_records = []
    for point in weak_points:
        today = datetime.now().date()
        exists = db.query(LearningRecord).filter(
            LearningRecord.student_id == current_user.id,
            LearningRecord.status.like(f"%{point}%"),
            LearningRecord.last_practice_date >= today
        ).first()

        if not exists:
            record = LearningRecord(
                student_id=current_user.id,
                knowledge_node_id=0,
                mastery_level=0.3, 
                last_practice_date=datetime.now(),
                status=f"AI诊断发现: {point}"
            )
            new_records.append(record)
    
    if new_records:
        db.add_all(new_records)
        db.commit()

    return {"weak_points": weak_points}

@router.post("/learning-path")
def generate_path(
    profile: StudentProfile, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据具体的薄弱点，生成学习路径
    """
    print(f"生成学习路径，目标: {profile.weak_subjects}")
    
    student_name = current_user.full_name or profile.name
    
    try:
        ai_result = ai_agent.generate_learning_path(
            student_profile={"name": student_name, "grade": str(profile.grade)},
            weak_points=profile.weak_subjects
        )
        return ai_result
    except Exception as e:
        print(f"AI 路径生成失败: {e}")
        return {"error": "服务连接失败", "path": []}

@router.get("/knowledge-graph/{course_id}")
def get_course_graph(course_id: int, db: Session = Depends(get_db)):
    nodes = db.query(KnowledgeNode).filter(KnowledgeNode.course_id == course_id).all()
    if not nodes: return {"nodes": [], "links": []}
    
    node_ids = [n.id for n in nodes]
    edges = db.query(KnowledgeEdge).filter(
        (KnowledgeEdge.source_id.in_(node_ids)) | (KnowledgeEdge.target_id.in_(node_ids))
    ).all()
    
    formatted_nodes = [
        {"id": str(n.id), "name": n.label, "symbolSize": 30 + (n.weight * 20), "category": 0, "value": n.weight} 
        for n in nodes
    ]
    formatted_edges = [
        {"source": str(e.source_id), "target": str(e.target_id), "label": {"show": True, "formatter": e.relation_type}} 
        for e in edges
    ]
    
    return {"nodes": formatted_nodes, "links": formatted_edges, "categories": [{"name": "知识点"}]}