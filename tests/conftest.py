"""Pytest fixtures and test environment setup."""

import os
import sqlite3
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

# Set test environment
os.environ["ENV"] = "test"
os.environ["USE_SQLITE_TEST"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from backend.app.core.database import Base, get_db
from backend.app.main import app

# Create in-memory SQLite test database engine
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)


@event.listens_for(test_engine, "connect")
def on_test_db_connect(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
    if isinstance(dbapi_connection, sqlite3.Connection):
        dummy_func = lambda *args: None
        dbapi_connection.create_function("GeomFromEWKT", -1, dummy_func)
        dbapi_connection.create_function("ST_GeomFromEWKT", -1, dummy_func)
        dbapi_connection.create_function("AsEWKB", -1, dummy_func)
        dbapi_connection.create_function("AsBinary", -1, dummy_func)
        dbapi_connection.create_function("CheckSpatialIndex", -1, dummy_func)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all database tables for the test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a transactional database session for a test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient with the test database dependency override."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
