from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import json

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
    grade: int
    weak_subjects: List[str]

@router.post("/learning-path")
def generate_path(
    profile: StudentProfile, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    接收学生薄弱点，调用豆包大模型生成学习路径，并存入数据库。
    """
    print(f"用户 {current_user.username} ({current_user.full_name}) 请求生成路径: {profile.weak_subjects}")
    
    student_name = current_user.full_name if current_user.full_name else profile.name
    
    try:
        ai_result = ai_agent.generate_learning_path(
            student_profile={"name": student_name, "grade": profile.grade},
            weak_points=profile.weak_subjects
        )
    except Exception as e:
        print(f"AI 调用失败: {e}")
        return {"error": "AI 服务连接失败", "details": str(e)}

    steps_str = json.dumps(ai_result.get("recommended_steps", []), ensure_ascii=False)
    
    new_record = LearningRecord(
        student_id=current_user.id,
        knowledge_node_id=0,        
        mastery_level=0.1,         
        status=f"AI规划: {profile.weak_subjects[0]}" 
    )
    
    db.add(new_record)
    db.commit()
    
    return ai_result

@router.get("/knowledge-graph/{course_id}")
def get_course_graph(course_id: int, db: Session = Depends(get_db)):
    nodes = db.query(KnowledgeNode).filter(KnowledgeNode.course_id == course_id).all()
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

@router.post("/generate-diagnostic-test")
def generate_diagnostic_test(grade: int, subject: str):
    """
    让 AI 生成一套包含主要知识点的诊断试卷
    """
    prompt = f"请为{grade}年级{subject}生成一套包含5道单选题的诊断测试，覆盖不同难度的核心知识点..."
    return ai_agent.generate_quiz(prompt)

@router.post("/analyze-diagnostic-result")
def analyze_diagnostic(answers: List[dict]):
    """
    分析错题，返回薄弱知识点列表
    """
    weak_points = ai_agent.analyze_weakness(answers) 
    return {"weak_points": weak_points}

class DiagnosticRequest(BaseModel):
    grade: int = 10
    subject: str = "数学"

class AnalyzeRequest(BaseModel):
    wrong_questions: List[dict] 

@router.post("/diagnostic/start")
def start_diagnostic(req: DiagnosticRequest, current_user: User = Depends(get_current_user)):
    print(f"为用户 {current_user.username} 生成诊断题...")
    questions = ai_agent.generate_diagnostic_quiz(req.grade, req.subject)
    return questions

@router.post("/diagnostic/analyze")
def analyze_diagnostic(req: AnalyzeRequest, current_user: User = Depends(get_current_user)):
    print(f"分析用户 {current_user.username} 的错题: {req.wrong_questions}")
    
    if not req.wrong_questions:
        return {"weak_points": ["暂无明显薄弱点（建议预习新课）"]}
        
    weak_points = ai_agent.analyze_weakness(req.wrong_questions)
    return {"weak_points": weak_points}