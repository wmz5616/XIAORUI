from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import shutil
import os
from datetime import datetime

# 引入本地模块
from ..models import SessionLocal, KnowledgeNode, KnowledgeEdge, LearningRecord, User, Course, CourseResource
from .auth import get_current_user # 鉴权

router = APIRouter(prefix="/teacher", tags=["Teacher End"])

def get_db():
    db = SessionLocal(); yield db; db.close()

# --- Pydantic 模型 ---
class CourseCreate(BaseModel):
    title: str
    description: str

class NodeCreate(BaseModel):
    course_id: int
    label: str
    weight: float = 1.0

class EdgeCreate(BaseModel):
    source_id: int
    target_id: int
    relation: str = "前置"

# 1. 获取班级学情
@router.get("/class-monitor")
def get_class_monitor(db: Session = Depends(get_db)):
    records = db.query(LearningRecord).all()
    if not records: return []
    result = []
    for r in records:
        student = db.query(User).filter(User.id == r.student_id).first()
        result.append({
            "id": r.student_id,
            "name": student.full_name if student else "未知",
            "weakness": r.status.replace("预警: ", "") if "预警" in r.status else "无",
            "progress": int(r.mastery_level * 100),
            "status": "Risk" if "预警" in r.status else "Normal"
        })
    return result

# 2. 创建课程 (新功能)
@router.post("/courses")
def create_course(course: CourseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != 'teacher':
        raise HTTPException(status_code=403, detail="权限不足")
        
    new_course = Course(
        title=course.title,
        description=course.description,
        teacher_id=current_user.id,
        status="published"
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return {"msg": "课程创建成功", "id": new_course.id, "title": new_course.title}

# 3. 获取我的课程列表
@router.get("/my-courses")
def get_teacher_courses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 简单演示：返回所有课程（实际应只返回该老师的）
    return db.query(Course).all()

# 4. 上传资源 (文件上传核心)
@router.post("/upload-resource")
async def upload_resource(
    course_id: int = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. 保存文件到本地 uploads 目录
    file_ext = file.filename.split(".")[-1]
    file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_path = f"uploads/{file_name}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. 写入数据库
    resource_type = "video" if file_ext in ['mp4', 'mov'] else "document"
    
    new_res = CourseResource(
        course_id=course_id,
        title=title,
        type=resource_type,
        url=f"http://localhost:8000/{file_path}" # 生成访问链接
    )
    db.add(new_res)
    db.commit()
    
    return {"msg": "上传成功", "url": new_res.url}

# --- 之前的图谱接口保留 ---
@router.post("/add-node")
def add_node(node: NodeCreate, db: Session = Depends(get_db)):
    new_node = KnowledgeNode(course_id=node.course_id, label=node.label, weight=node.weight)
    db.add(new_node); db.commit(); db.refresh(new_node)
    return {"msg": "添加成功", "node_id": new_node.id}

@router.post("/add-edge")
def add_edge(edge: EdgeCreate, db: Session = Depends(get_db)):
    new_edge = KnowledgeEdge(source_id=edge.source_id, target_id=edge.target_id, relation_type=edge.relation)
    db.add(new_edge); db.commit()
    return {"msg": "关联成功"}

@router.get("/course-nodes/{course_id}")
def get_nodes_list(course_id: int, db: Session = Depends(get_db)):
    nodes = db.query(KnowledgeNode).filter(KnowledgeNode.course_id == course_id).all()
    return [{"id": n.id, "label": n.label} for n in nodes]