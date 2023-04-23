# HTTP 요청을 받아서 처리하고 결과를 반환
from fastapi import APIRouter
import logging
from . import services
from .models import CommentCreate 

logger = logging.getLogger('post_server_logger')
router = APIRouter()

@router.get("/comments")
def get_all_comments():
    logger.debug("new request: GET /comments")
    """
    게시글 전체 조회 엔드포인트
    """
    return services.get_all_posts()

@router.post("/comments")
def create_comment(post: CommentCreate):  
    logger.debug("new request: POST /comments")
    """
    게시글 생성 엔드포인트
    """
    return services.create_comment(comment)

