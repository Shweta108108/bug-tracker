import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.db import get_db
from app.main import app

settings = get_settings()
ALEMBIC_INI = str(Path(__file__).resolve().parent.parent / "alembic.ini")


@pytest.fixture(scope="session")
def db_engine():
    os.environ["ALEMBIC_DATABASE_URL"] = settings.test_database_url
    alembic_cfg = Config(ALEMBIC_INI)
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(settings.test_database_url)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> Session:
    connection = db_engine.connect()
    outer_transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = session_factory()

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
