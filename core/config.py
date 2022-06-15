import enum
from typing import Optional

from pydantic import BaseSettings
from sqlalchemy.engine.url import URL
import warnings


class Language(str, enum.Enum):
    """
    Supported language code
    """

    English = "en_GB"
    Chinese = "zh_CN"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Necktie"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    DB_DRIVER: str = "sqlite+aiosqlite"
    DB_HOST: str = ""
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_DATABASE: str = "necktie.db"

    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 0
    DB_ECHO: bool = False

    @property
    def DB_DSN(self) -> URL:
        return URL.create(
            self.DB_DRIVER,
            self.DB_USER,
            self.DB_PASSWORD,
            self.DB_HOST,
            self.DB_PORT,
            self.DB_DATABASE,
        )

    class Config:
        case_sensitive = True


settings = Settings()

# Ingore unecessary warnings that happen with sqlite
warnings.filterwarnings("ignore", ".*SELECT*")
warnings.filterwarnings("ignore", ".*Dialect*")
