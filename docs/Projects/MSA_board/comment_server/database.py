# 데이터베이스와의 연결을 설정
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings
import logging

logger = logging.getLogger("comment_server_logger")

db_url = f"mysql+mysqlconnector://{settings.db_username}:{settings.db_password}@{settings.db_host}/{settings.db_name}"

engine = create_engine(
    db_url,
    pool_size=5, # 최소 커넥션
    max_overflow=10, # 최대 커넥션
    pool_pre_ping=True # 커넥션 풀에서 커넥션을 가져오기 전에 ping을 한 번 날려서 유효한지 확인하고 에러 방지
)
logger.debug("created: DB handler")
metadata = MetaData()
Base = declarative_base(metadata=metadata)
SessionLocal = sessionmaker(bind=engine)

metadata.bind = engine
 
def initialize():
    try:
        logger.debug("creating: new table")
        Base.metadata.create_all(engine)
    except:
        logger.info("skip table creation: table already exists" )

