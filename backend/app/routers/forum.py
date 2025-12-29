from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

# 引入本地模块
from ..models import SessionLocal, ForumPost, User
from .auth import get_current_user # 引入鉴权，确保只有登录用户能发帖

router = APIRouter(prefix="/forum", tags=["Forum"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic 模型 ---
class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_name: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 1. 获取所有帖子 (按时间倒序)
@router.get("/posts", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(ForumPost).order_by(ForumPost.created_at.desc()).all()
    
    # 组装返回数据，带上作者名字
    results = []
    for p in posts:
        author = db.query(User).filter(User.id == p.author_id).first()
        results.append({
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "author_name": author.full_name if author else "未知用户",
            "role": author.role if author else "student",
            "created_at": p.created_at
        })
    return results

# 2. 发布新帖子 (需要登录)
@router.post("/posts")
def create_post(post: PostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    print(f"用户 {current_user.username} 正在发帖: {post.title}")
    
    new_post = ForumPost(
        title=post.title,
        content=post.content,
        author_id=current_user.id,
        type="discussion"
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"msg": "发布成功", "id": new_post.id}