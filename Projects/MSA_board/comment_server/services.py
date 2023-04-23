from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal
import logging

logger = logging.getLogger("comment_server_logger")

def get_db():
    """
    get_db 호출하는 쪽에서 with 구문으로 호출해서 사용하면 된다
    """
    logger.debug("creating: new DB connection")
    db = SessionLocal() #SessionLocal은 sessionmaker 인스턴스
    # try:
    #     yield db # 적용 실패
    # finally: #호출하는 쪽의 with 구문이 종료되면 finally구문이 실행됨(db session 종료)
    #     logger.debug("closing DB connection")
    #     db.close()
    return db

def get_comments(postId: int):
    """
    게시글 전체 조회를 위한 함수
    """
    logger.debug(f"trying: get all comments from DB for postId={postId}")
    with get_db() as db:
        records = db.query(models.Comment).filter(models.Comment.post_number == postId).all()
        for record in records:
            logger.debug(record.__dict__)
        return records


def create_comment(comment_request: models.CommentCreate): 
    with get_db() as db: # with 구문을 사용해 연결이 끝나면 자동으로 종료
        logger.debug(comment_request)
        comment_instance = models.Comment(**comment_request.dict()) # comment_request.dict로 CommentCreate 모델 인스턴스의 데이터를 dict로 변환하고 이를 Comment 모델 인스턴스 생성에 사용
        logger.debug("created: insert new comment to DB")
        db.add(comment_instance)
        db.commit()
        logger.debug("return: db.commit")
        db.refresh(comment_instance)
        logger.debug("return: db.refresh")
        return comment_instance
