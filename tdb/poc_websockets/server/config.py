import sys
from pathlib import Path

from pydantic.networks import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationConfig(BaseSettings):
    VERSION: str
    PROJECT_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_ECHO: bool
    POSTGRES_POOL_SIZE: int
    ASYNC_POSTGRES_URI: PostgresDsn
    ENV: str
    APP_HOST: str
    APP_PORT: int
    APP_SCHEMA: str
    LOG_LEVEL: str = 'DEBUG'

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DIR: Path = Path.cwd()
    LOGS: Path = DIR / 'logs'

    RESOURCES: Path = DIR / 'resources'
    HTML: Path = RESOURCES / 'html'
    STATIC: Path = RESOURCES / 'static'
    TEMPLATES: Path = RESOURCES / 'templates'

    LAUNCH_FILE: str = Path(sys.argv[0]).stem

    model_config = SettingsConfigDict(case_sensitive=True)

    def __init__(self, *, setup_logging: bool = True) -> None:
        from tdb.poc_websockets.server import logger

        super().__init__()

        if setup_logging:
            logger.setup_logging(self.LOG_LEVEL, file_name=str(self.LOGS / f'{self.LAUNCH_FILE}.log'))


# Requires all Setting variables to exist in env
settings = ApplicationConfig()
