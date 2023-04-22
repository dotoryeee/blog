from pydantic import BaseSettings

class Settings(BaseSettings):
    db_username: str
    db_password: str
    db_host: str
    db_name: str

    class Config:
        env_file = "app/config.env"
        env_file_encoding = "utf-8"

settings = Settings() #인스턴스를 생성하여 유효성 검사를 수행할 수 있다
