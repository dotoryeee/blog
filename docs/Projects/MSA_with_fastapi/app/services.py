from sqlalchemy.orm import Session
from . import models
from .models import Post
from .database import SessionLocal
import logging

logger = logging.getLogger("post_server_logger")

def get_db():
    """
    get_db 호출하는 쪽에서 with 구문으로 호출해서 사용하면 된다
    """
    logger.debug("creating: new DB connection")
    db = SessionLocal() #SessionLocal은 sessionmaker 인스턴스
    logger.debug("created: new DB connection")
    # try:
    #     yield db 적용 실패
    # finally: #호출하는 쪽의 with 구문이 종료되면 finally구문이 실행됨(db session 종료)
    #     logger.debug("closing DB connection")
    #     db.close()
    return db

def get_all_posts():
    """
    게시글 전체 조회를 위한 함수
    """
    logger.debug("trying: get all posts from DB")
    with get_db() as db:
        logger.debug("created: get all posts")
        return db.query(models.Post).all()

def create_post(post: Post):
    """
    게시글 생성을 위한 함수
    """
    with get_db() as db:
        logger.debug("created: insert new post to DB")
        db.add(post)
        db.commit()
        logger.debug("return: db.commit")
        db.refresh(post)
        logger.debug("return: db.refresh")
        return post
