from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

db_url = f"mysql+mysqlconnector://{settings.db_username}:{settings.db_password}@{settings.db_host}/{settings.db_name}"

engine = create_engine(
    db_url, pool_size=10, max_overflow=20, pool_pre_ping=True
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