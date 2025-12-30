from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from ..models import SessionLocal, ForumPost, User
from .auth import get_current_user

router = APIRouter(prefix="/forum", tags=["Forum"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_name: str
    role: str
    is_pinned: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/posts", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(ForumPost).order_by(
        ForumPost.is_pinned.desc(), 
        ForumPost.created_at.desc()
    ).all()
    
    results = []
    for p in posts:
        author = db.query(User).filter(User.id == p.author_id).first()
        results.append({
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "author_name": author.full_name if author else "未知用户",
            "role": author.role if author else "student",
            "is_pinned": p.is_pinned,
            "created_at": p.created_at
        })
    return results

@router.post("/posts")
def create_post(post: PostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_silenced:
        raise HTTPException(status_code=403, detail="您已被禁言，无法发布内容")
    
    new_post = ForumPost(
        title=post.title,
        content=post.content,
        author_id=current_user.id,
        type="discussion",
        is_pinned=False
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"msg": "发布成功", "id": new_post.id}

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ['teacher', 'admin']:
        raise HTTPException(status_code=403, detail="权限不足")
        
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
        
    db.delete(post)
    db.commit()
    return {"msg": "已删除"}

@router.put("/posts/{post_id}/pin")
def toggle_pin(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ['teacher', 'admin']:
        raise HTTPException(status_code=403, detail="权限不足")
        
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if post:
        post.is_pinned = not post.is_pinned
        db.commit()
    return {"msg": "操作成功", "current_status": post.is_pinned}