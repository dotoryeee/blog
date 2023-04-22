from sqlalchemy.orm import Session
from . import models
from .models import Post
from .database import SessionLocal

"""
TypeError: 'generator' object does not support the context manager protocol
-> get_db 호출하는 쪽에서 async with 구문으로 호출해서 사용하면 된다
"""

def get_db():
    """
    get_db 호출하는 쪽에서 with(x) -> async with 구문으로 호출해서 사용하면 된다
    """
    db = SessionLocal() #SessionLocal은 sessionmaker 인스턴스
    try:
        yield db
    finally: #호출하는 쪽의 with 구문이 종료되면 finally구문이 실행됨(db session 종료)
        db.close()

async def get_all_posts():
    """
    게시글 전체 조회를 위한 함수
    """
    async with get_db() as db:
        return db.query(models.Post).all()

async def create_post(post: Post):
    """
    게시글 생성을 위한 함수
    """
    async with get_db() as db:
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post
