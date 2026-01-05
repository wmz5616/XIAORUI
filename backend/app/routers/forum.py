from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..models import SessionLocal, ForumPost, User, PostLike, ForumReply
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

class ReplyCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None

class ReplyResponse(BaseModel):
    id: int
    content: str
    author_name: str
    role: str
    created_at: datetime
    parent_id: Optional[int]
    is_hidden: bool
    
    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_name: str
    role: str
    is_pinned: bool
    created_at: datetime
    like_count: int
    reply_count: int
    is_liked: bool
    replies: List[ReplyResponse] = []
    
    class Config:
        from_attributes = True

@router.get("/posts", response_model=List[PostResponse])
def get_posts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    posts = db.query(ForumPost).order_by(
        ForumPost.is_pinned.desc(), 
        ForumPost.created_at.desc()
    ).all()
    
    results = []
    for p in posts:
        like_count = db.query(PostLike).filter(PostLike.post_id == p.id).count()
        
        user_like = db.query(PostLike).filter(
            PostLike.post_id == p.id, 
            PostLike.user_id == current_user.id
        ).first()
        
        replies_db = db.query(ForumReply).filter(
            ForumReply.post_id == p.id
        ).order_by(ForumReply.created_at.asc()).all()
        
        replies_fmt = []
        for r in replies_db:
            if r.is_hidden and current_user.role == 'student' and r.author_id != current_user.id:
                continue

            r_author = db.query(User).filter(User.id == r.author_id).first()
            replies_fmt.append({
                "id": r.id,
                "content": r.content,
                "author_name": r_author.full_name if r_author else "未知用户",
                "role": r_author.role if r_author else "student",
                "created_at": r.created_at,
                "parent_id": r.parent_id,
                "is_hidden": r.is_hidden
            })

        author = db.query(User).filter(User.id == p.author_id).first()
        
        results.append({
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "author_name": author.full_name if author else "未知用户",
            "role": author.role if author else "student",
            "is_pinned": p.is_pinned,
            "created_at": p.created_at,
            "like_count": like_count,
            "reply_count": len(replies_fmt),
            "is_liked": bool(user_like),
            "replies": replies_fmt
        })
    return results

@router.post("/posts")
def create_post(post: PostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_silenced:
        raise HTTPException(status_code=403, detail="您已被禁言")
    
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
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    is_owner = current_user.id == post.author_id
    is_manager = current_user.role in ['teacher', 'admin']
    
    if not (is_owner or is_manager):
        raise HTTPException(status_code=403, detail="权限不足")
        
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
    return {"msg": "帖子不存在"}

@router.post("/posts/{post_id}/like")
def toggle_like(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(PostLike).filter(
        PostLike.post_id == post_id, 
        PostLike.user_id == current_user.id
    ).first()
    
    if existing:
        db.delete(existing)
        msg = "取消点赞"
        liked = False
    else:
        new_like = PostLike(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        msg = "点赞成功"
        liked = True
        
    db.commit()
    return {"msg": msg, "is_liked": liked}

@router.post("/posts/{post_id}/reply")
def create_reply(post_id: int, reply: ReplyCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_silenced:
        raise HTTPException(status_code=403, detail="您已被禁言")
        
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    new_reply = ForumReply(
        post_id=post_id, 
        author_id=current_user.id, 
        content=reply.content,
        parent_id=reply.parent_id,
        is_hidden=False
    )
    db.add(new_reply)
    db.commit()
    return {"msg": "回复成功"}

@router.put("/replies/{reply_id}/hide")
def toggle_reply_hide(reply_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ['teacher', 'admin']:
        raise HTTPException(status_code=403, detail="权限不足")
        
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="评论不存在")
        
    reply.is_hidden = not reply.is_hidden
    db.commit()
    return {"msg": "操作成功", "is_hidden": reply.is_hidden}

@router.delete("/replies/{reply_id}")
def delete_reply(reply_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="评论不存在")
        
    is_owner = current_user.id == reply.author_id
    is_manager = current_user.role in ['teacher', 'admin']
    
    if not (is_owner or is_manager):
        raise HTTPException(status_code=403, detail="权限不足")
        
    db.delete(reply)
    db.commit()
    return {"msg": "已删除"}