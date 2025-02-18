from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel
from ..core.config import settings
from app.core.db import get_engine
from app.main import app


@pytest.fixture(scope="package")
def db() -> Generator[Session, None, None]:
    """
    before crud tests:
        docker exec -it test_task_db \
        psql -U postgres \
        -c "CREATE DATABASE test_database;"

    after:
        docker exec -it test_task_db \
        psql -U postgres \
        -c "DROP DATABASE test_database;"
    """

    settings.ENVIRONMENT = "testing"
    engine = get_engine(echo=True)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(scope="package")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
