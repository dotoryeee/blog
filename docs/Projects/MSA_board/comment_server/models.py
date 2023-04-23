# 데이터베이스 테이블과 관련된 모델 클래스를 정의
from sqlalchemy import Column, Integer, DateTime, Text
from .database import Base
from datetime import datetime
from pydantic import BaseModel

# sqlalchemy의 모델 클래스인 Base 클래스를 상속받아서 Comment 모델 클래스를 정의합니다
class Comment(Base):
    __tablename__ = "comments" # 테이블 이름을 "comments"로 설정합니다

    id = Column(Integer, primary_key=True, index=True) # 정수형 id컬럼을 추가하고 기본키로 설정합니다.
    post_number = Column(Integer, index=True) # Comment의 원본 post 정보
    comment = Column(Text, nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow)

# 사용자로부터 입력받은 Post를 담을 모델
class CommentCreate(BaseModel):
    title: str
    post_number: int
    content: str
