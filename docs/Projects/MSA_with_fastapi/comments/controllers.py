from fastapi import APIRouter
from . import services
from .models import Comment

router = APIRouter()

@router.get("/comments/{post_id}")
def get_comments(post_id: int):
    return services.get_comments_by_post(post_id)

@router.post("/comments/{post_id}")
def create_comment(post_id: int, comment: Comment):
    return services.create_comment(post_id, comment)
