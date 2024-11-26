import os

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine, AsyncSession)
from sqlalchemy.orm import DeclarativeBase
import logging


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra="allow")
    DEBUG: bool = True

    DB_USER: str = 'postgres'
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "db_info_hub"

    SECRET_KEY: str = "secret_key-123"

    LOG_DIR: str = "./logs"
    LOG_NAME: str = 'project_log'

    def init_loger(self):
        if settings_app.DEBUG:
            level_log = logging.INFO
        else:
            level_log = 30

        logging.basicConfig(
            level=level_log,
            format="[%(asctime)s] /%(filename)s:%(lineno)d / %(levelname)s - %(name)s -- %(message)s",
            filename=f"{self.LOG_DIR}/{self.LOG_NAME}.txt",
            filemode="a"
        )

        log = logging.getLogger(name=self.LOG_NAME)
        log.setLevel(level_log)
        return log

    def pg_dsn(self, engine_="asyncpg") -> PostgresDsn:
        return (
            f"postgresql+{engine_}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"localhost:5432/{self.DB_NAME}")

    def sqlite_dsn(self) -> str:
        return f"sqlite+aiosqlite:///./{self.DB_NAME}.db"


settings_app = Settings()

if not os.path.exists(settings_app.LOG_DIR):
    os.makedirs(settings_app.LOG_DIR)

logger = settings_app.init_loger()

DATABASE_URL = settings_app.sqlite_dsn()
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session() as sess:
        yield sess
