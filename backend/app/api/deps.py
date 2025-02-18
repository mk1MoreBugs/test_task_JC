from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from sqlmodel import Session

from app.core.config import settings
from app.core.db import get_engine


def get_db() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
