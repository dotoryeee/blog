from fastapi import FastAPI
from . import controllers

app = FastAPI()

# 게시글 controller를 app에 포함
app.include_router(controllers.router)
