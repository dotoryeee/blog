# 데이터베이스 테이블과 관련된 모델 클래스를 정의
from sqlalchemy import Column, Integer, String, DateTime, Text
from .database import Base
from datetime import datetime

# sqlalchemy의 모델 클래스인 Base 클래스를 상속받아서 Post 모델 클래스를 정의합니다
class Post(Base):
    __tablename__ = "posts" # 테이블 이름을 "posts"로 설정합니다

    id = Column(Integer, primary_key=True, index=True) # 정수형 id컬럼을 추가하고 기본키로 설정합니다.
    title = Column(String(255), nullable=False) 
    content = Column(Text, nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow) 

