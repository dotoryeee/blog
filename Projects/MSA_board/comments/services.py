from sqlalchemy.orm import Session
from . import models
from .models import Comment
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_comments_by_post(post_id: int):
    with get_db() as db:
        return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()

def create_comment(post_id: int, comment: Comment):
    with get_db() as db:
        comment.post_id = post_id
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
