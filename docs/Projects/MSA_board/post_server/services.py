from sqlalchemy.orm import Session
from . import models
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
    #     yield db # 적용 실패
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


def create_post(post_request: models.PostCreate): 
    with get_db() as db: # with 구문을 사용해 연결이 끝나면 자동으로 종료
        logger.debug(post_request)
        post_instance = models.Post(**post_request.dict()) # post_request.dict로 PostCreate 모델 인스턴스의 데이터를 dict로 변환하고 이를 Post 모델 인스턴스 생성에 사용
        logger.debug("created: insert new post to DB")
        db.add(post_instance)
        db.commit()
        logger.debug("return: db.commit")
        db.refresh(post_instance)
        logger.debug("return: db.refresh")
        return post_instance
