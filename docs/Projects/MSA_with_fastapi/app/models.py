from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

# sqlalchemy의 모델 클래스인 Base 클래스를 상속받아서 Post 모델 클래스를 정의합니다
class Post(Base):
    __tablename__ = "posts" # 테이블 이름을 "posts"로 설정합니다

    id = Column(Integer, primary_key=True, index=True) # 정수형 id컬럼을 추가하고 기본키로 설정합니다.
    title = Column(String, index=True) # 문자열 컬럼인 title을 생성하고 추후 제목 기반으로 빠른 검색을 위해 인덱스로 설정합니다
    content = Column(String) # 문자열 컬럼인 content를 추가합니다
    created_at = Column(DateTime) # created_at 컬럼을 생성하고 DateTime 클래스를 사용하여 시간 정보를 저장할 수 있도록 합니다
