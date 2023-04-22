from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

db_url = f"mysql+mysqlconnector://{settings.db_username}:{settings.db_password}@{settings.db_host}/{settings.db_name}"

engine = create_engine(
    db_url,
    pool_size=5, # 최소 커넥션
    max_overflow=10, # 최대 커넥션
    pool_pre_ping=True # 커넥션 풀에서 커넥션을 가져오기 전에 ping을 한 번 날려서 유효한지 확인하고 에러 방지
)
metadata = MetaData()
Base = declarative_base(metadata=metadata)
SessionLocal = sessionmaker(bind=engine)

metadata.bind = engine
 
"""
최신 버전의 sqlalchemy에서는 bind대신 bind_to를 사용하고, metadata대신 metadata=None을 사용
따라서 metadata의 bind 메서드와 engine을 연결
declarative_base 함수는 metadata 인수에 metadata=None을 사용하여 metadata객체를 인수로 받도록 수정
"""