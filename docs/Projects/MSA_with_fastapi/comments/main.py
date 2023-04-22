from fastapi import FastAPI
from . import controllers

app = FastAPI()

app.include_router(controllers.router)
