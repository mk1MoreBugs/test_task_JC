import os
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str
    PROJECT_VERSION: str = "0.0.1"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: Literal["dev", "testing", "migration", "staging", "production"] = "dev"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]


    @property
    def POSTGRES_SERVER(self) -> str:
        if self.ENVIRONMENT == "testing" or self.ENVIRONMENT == "migration":
            return "localhost"
        else:
            return self.POSTGRES_SERVER

    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str

    @staticmethod
    def __get_postgres_password():
        path = os.getenv("POSTGRES_PASSWORD_FILE")
        if path is None:
            path = "../db_password.txt"
        with open(path, encoding="utf-8") as f:
            return f.readline()

    POSTGRES_PASSWORD: str = __get_postgres_password()

    @property
    def POSTGRES_DB(self) -> str:
        if self.ENVIRONMENT == "testing":
            return "test_database"
        else:
            return self.POSTGRES_DB


    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if (self.ENVIRONMENT == "dev"
                    or self.ENVIRONMENT == "testing"
                    or self.ENVIRONMENT == "migration"):
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        return self


settings = Settings()  # type: ignore
