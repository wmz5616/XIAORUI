from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import json

# 导入本地模块
from ..models import SessionLocal, KnowledgeNode, KnowledgeEdge, LearningRecord

from ..services.doubao_ai import ai_agent

router = APIRouter(prefix="/ai-engine", tags=["AI Core"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic 模型 ---
class StudentProfile(BaseModel):
    name: str
    grade: int
    weak_subjects: List[str]

# ================= 接口 1: 生成个性化学习路径 (修复 404) =================
@router.post("/learning-path")
def generate_path(profile: StudentProfile, db: Session = Depends(get_db)):
    """
    前端请求地址变为: POST /ai-engine/learning-path
    """
    print(f"AI Engine 收到请求: {profile.weak_subjects}")
    
    # 1. 调用 AI
    try:
        ai_result = ai_agent.generate_learning_path(
            student_profile={"name": profile.name, "grade": profile.grade},
            weak_points=profile.weak_subjects
        )
    except Exception as e:
        # 防止 AI 服务未启动导致报错
        print(f"AI 调用失败: {e}")
        return {"error": "AI 服务连接失败", "details": str(e)}
    
    # 2. 保存记录 (模拟绑定学生 ID=1)
    # 将步骤列表转为字符串存储
    steps_str = json.dumps(ai_result.get("recommended_steps", []), ensure_ascii=False)
    
    new_record = LearningRecord(
        student_id=1, 
        knowledge_node_id=0, # 暂无特定节点
        mastery_level=0.2,   # 初始掌握度低
        status=f"预警: {profile.weak_subjects[0]}" 
    )
    
    db.add(new_record)
    db.commit()
    
    return ai_result

# ================= 接口 2: 获取知识图谱 =================
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