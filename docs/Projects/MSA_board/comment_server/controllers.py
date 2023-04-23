# HTTP 요청을 받아서 처리하고 결과를 반환
from fastapi import APIRouter
import logging
from . import services
from .models import CommentCreate 

logger = logging.getLogger('post_server_logger')
router = APIRouter()

@router.get("/comments")
def get_comments(postId: int=None):
    logger.debug(f"new request: GET /comments/postId={postId}")
    """
    게시글 전체 조회 엔드포인트
    """
    return None if postId is None else services.get_comments(postId)

@router.post("/comments")
def create_comment(postId: int, comment: CommentCreate):  
    logger.debug(f"new request: POST /comments")
    """
    게시글 생성 엔드포인트
    """
    return services.create_comment(postId, comment)

