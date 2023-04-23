# HTTP 요청을 받아서 처리하고 결과를 반환
from fastapi import APIRouter
import logging
from . import services
from .models import PostCreate 

logger = logging.getLogger('post_server_logger')
router = APIRouter()

@router.get("/posts")
def get_all_posts():
    logger.debug("new request: GET /posts")
    """
    게시글 전체 조회 엔드포인트
    """
    return services.get_all_posts()

@router.post("/posts")
def create_post(post: PostCreate):  
    logger.debug("new request: POST /posts")
    """
    게시글 생성 엔드포인트
    """
    return services.create_post(post)

