# 앱의 진입점, FastAPI 인스턴스를 생성하고 라우팅을 설정하는 역할
# uvicorn post_server.main:app --host 0.0.0.0 --port 8000
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import controllers, database
import logging

app = FastAPI()

# 게시글 controller를 app에 포함
app.include_router(controllers.router)

# logging.basicConfig(filename="post-server.log")
logger = logging.getLogger("post_server_logger")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# 데이터베이스 초기화
database.initialize()

# CORS option
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처를 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용
    allow_headers=["*"],  # 모든 HTTP 헤더를 허용
)
