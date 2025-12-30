from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

# 引入本地模块
from ..models import SessionLocal, Course, CourseResource, KnowledgeNode, KnowledgeEdge, User, LearningRecord
from .auth import get_current_user # 引入鉴权，确保能获取当前登录用户

router = APIRouter(prefix="/student", tags=["Student Learning"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 模型定义 ---
class CourseModel(BaseModel):
    id: int
    title: str
    description: str
    teacher_name: str = "未知教师"

    class Config:
        from_attributes = True

class ResourceModel(BaseModel):
    id: int
    title: str
    type: str
    url: str

class UserProfile(BaseModel):
    username: str
    full_name: str
    role: str
    learn_time: int       # 学习时长(分钟)
    finished_courses: int # 完成课程数
    ability_radar: List[int] # 五维能力值

# 1. 获取所有可选课程 (首页展示用)
@router.get("/courses", response_model=List[CourseModel])
def get_all_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.status == "published").all()
    return courses

# 2. 获取课程详情与资源列表 (学习教室用)
@router.get("/course/{course_id}/resources", response_model=List[ResourceModel])
def get_course_resources(course_id: int, db: Session = Depends(get_db)):
    # 验证课程是否存在
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # 获取资源
    resources = db.query(CourseResource).filter(CourseResource.course_id == course_id).all()
    return resources

# 3. 获取知识图谱 (真实数据版：支持变色)
@router.get("/knowledge-graph/{course_id}")
def get_knowledge_graph(
    course_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 关键：获取当前用户
):
    # A. 获取课程结构
    nodes = db.query(KnowledgeNode).filter(KnowledgeNode.course_id == course_id).all()
    if not nodes:
        return {"nodes": [], "links": [], "categories": []}
        
    # 获取涉及到的节点ID列表
    node_ids = [n.id for n in nodes]
    
    # 只查询两端都在该课程内的边
    links = db.query(KnowledgeEdge).filter(
        KnowledgeEdge.source_id.in_(node_ids),
        KnowledgeEdge.target_id.in_(node_ids)
    ).all()

    # B. 获取该学生的学习记录 (用于判断节点颜色)
    records = db.query(LearningRecord).filter(
        LearningRecord.student_id == current_user.id
    ).all()
    
    # 构建掌握状态字典 {node_id: True/False}
    # 判定标准：mastery_level >= 0.8 视为掌握
    mastered_map = {r.knowledge_node_id: (r.mastery_level >= 0.8) for r in records}

    # C. 组装节点数据
    formatted_nodes = []
    for n in nodes:
        is_mastered = mastered_map.get(n.id, False)
        formatted_nodes.append({
            "id": str(n.id),
            "name": n.label,
            "symbolSize": n.weight * 30 + 10, # 根据权重调整大小
            "category": 1 if is_mastered else 0, # 1=绿色(已掌握), 0=红色(未掌握)
            "draggable": True,
            "value": n.weight
        })

    # D. 组装边数据
    formatted_links = [
        {"source": str(l.source_id), "target": str(l.target_id)} 
        for l in links
    ]

    return {
        "nodes": formatted_nodes,
        "links": formatted_links,
        "categories": [{"name": "未掌握", "color": "#F56C6C"}, {"name": "已掌握", "color": "#67C23A"}]
    }

# 4. 获取学生个人画像 (真实数据版)
@router.get("/profile", response_model=UserProfile)
def get_student_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # A. 查询真实掌握的知识点数量
    mastered_count = db.query(LearningRecord).filter(
        LearningRecord.student_id == current_user.id,
        LearningRecord.mastery_level >= 0.8
    ).count()

    # B. 动态计算能力值 (不再是随机数)
    # 算法：基础分40 + (掌握知识点数 * 15)，最高100分
    base_score = 40
    dynamic_score = min(100, base_score + (mastered_count * 15))
    
    # 简单模拟五维差异 (实际可根据知识点类型细分)
    radar_data = [
        dynamic_score,              # 记忆
        min(100, dynamic_score + 10), # 理解
        min(100, dynamic_score - 5),  # 应用
        min(100, dynamic_score + 5),  # 分析
        dynamic_score               # 创造
    ]
    
    # C. 获取真实数据
    # learn_time 字段已在数据库模型更新中添加
    real_learn_time = getattr(current_user, 'learn_time', 0)

    return {
        "username": current_user.username,
        "full_name": current_user.full_name or "未命名",
        "role": current_user.role,
        "learn_time": real_learn_time, 
        "finished_courses": int(mastered_count / 3), # 估算：每掌握3个知识点 ≈ 完成1门微课
        "ability_radar": radar_data
    }