from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

DATABASE_URL = f"mysql+mysqlconnector://{settings.db_username}:{settings.db_password}@{settings.db_host}/{settings.db_name}"

engine = create_engine(DATABASE_URL)
metadata = MetaData(bind=engine)
Base = declarative_base(metadata=metadata)
SessionLocal = sessionmaker(bind=engine)
