from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Path
from fastapi.openapi.models import Example

from sqlmodel import Session

from app.core.db import get_engine


def get_db() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

WalletUuid = Annotated[
    UUID,
    Path(
        description="wallet UUID",
        openapi_examples={"normal": Example(value="e58ed763-928c-4155-bee9-fdbaaadc15f3")}
    )
]
