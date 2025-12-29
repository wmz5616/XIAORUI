from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

# 引入本地模块
from ..models import SessionLocal, Course, CourseResource, KnowledgeNode, KnowledgeEdge, User
from .auth import get_current_user # 鉴权

router = APIRouter(prefix="/student", tags=["Student Learning"])

def get_db():
    db = SessionLocal(); yield db; db.close()

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
    ability_radar: List[int] # 五维能力值 [80, 60, 70, 90, 50]

# 1. 获取所有可选课程 (首页展示用)
@router.get("/courses", response_model=List[CourseModel])
def get_all_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).filter(Course.status == "published").all()
    # 简单处理：不连表查询，直接返回
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

# --- 之前的图谱接口保留 ---
@router.get("/knowledge-graph/{course_id}")
def get_knowledge_graph(course_id: int, db: Session = Depends(get_db)):
    nodes = db.query(KnowledgeNode).filter(KnowledgeNode.course_id == course_id).all()
    links = db.query(KnowledgeEdge).all() # 简化：返回所有连线
    
    return {
        "nodes": [{"id": str(n.id), "name": n.label, "symbolSize": n.weight * 30 + 10} for n in nodes],
        "links": [{"source": str(l.source_id), "target": str(l.target_id)} for l in links]
    }

@router.get("/profile", response_model=UserProfile)
def get_student_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. 基础信息
    # 2. 统计数据 (此处为简单模拟，实际应从 LearningRecord 表计算)
    # 模拟逻辑：根据用户 ID 生成一些伪随机数据，保证每个人不一样
    base_score = (current_user.id * 10) % 40 + 50 # 50-90分之间
    
    return {
        "username": current_user.username,
        "full_name": current_user.full_name or "未命名",
        "role": current_user.role,
        "learn_time": 120 + current_user.id * 5, # 模拟时长
        "finished_courses": 2,
        # 模拟五维能力：[记忆, 理解, 应用, 分析, 创造]
        "ability_radar": [
            base_score, 
            base_score + 5, 
            90, 
            base_score - 10, 
            80
        ]
    }