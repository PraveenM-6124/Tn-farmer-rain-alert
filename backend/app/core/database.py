"""Database configuration, engine setup, and session lifecycle management."""

import os
import sqlite3
from collections.abc import Generator

from geoalchemy2 import Geometry
from geoalchemy2.admin.dialects import sqlite as geo_sqlite
from sqlalchemy import create_engine, event
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.app.core.config import settings


# SQLite compatibility compiler for testing environments without SpatiaLite
@compiles(Geometry, "sqlite")
def compile_geometry_sqlite(element, compiler, **kw):  # type: ignore[no-untyped-def]
    return "BLOB"


# Disable SpatiaLite DDL triggers in SQLite test environments
if hasattr(geo_sqlite, "before_create"):
    geo_sqlite.before_create = lambda table, bind, **kw: None  # type: ignore[assignment]
if hasattr(geo_sqlite, "after_create"):
    geo_sqlite.after_create = lambda table, bind, **kw: None  # type: ignore[assignment]
if hasattr(geo_sqlite, "before_drop"):
    geo_sqlite.before_drop = lambda table, bind, **kw: None  # type: ignore[assignment]
if hasattr(geo_sqlite, "after_drop"):
    geo_sqlite.after_drop = lambda table, bind, **kw: None  # type: ignore[assignment]


def get_engine_url() -> str:
    """Determine database URL with fallback handling."""
    db_url = settings.DATABASE_URL
    # In test mode or when requested via env
    if settings.ENV == "test" or os.environ.get("USE_SQLITE_TEST", "").lower() == "true":
        return "sqlite:///:memory:"
    return db_url


# Configure engine
connect_args = {}
database_url = get_engine_url()
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)


# Register dummy spatial SQLite functions for test environments
@event.listens_for(engine, "connect")
def on_db_connect(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
    if isinstance(dbapi_connection, sqlite3.Connection):

        def dummy_func(*args):  # type: ignore[no-untyped-def]
            return None

        dbapi_connection.create_function("GeomFromEWKT", -1, dummy_func)
        dbapi_connection.create_function("ST_GeomFromEWKT", -1, dummy_func)
        dbapi_connection.create_function("AsEWKB", -1, dummy_func)
        dbapi_connection.create_function("AsBinary", -1, dummy_func)
        dbapi_connection.create_function("CheckSpatialIndex", -1, dummy_func)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and safely closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
