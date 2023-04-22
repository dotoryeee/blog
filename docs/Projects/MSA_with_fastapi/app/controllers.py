from fastapi import APIRouter
from . import services
from .models import Post

router = APIRouter()

@router.get("/posts")
def get_all_posts():
    """
    게시글 전체 조회 엔드포인트
    """
    return services.get_all_posts()

@router.put("/posts")
def create_post(post):
    """
    게시글 생성 엔드포인트
    """
    return services.create_post(post)
