from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


_EXTRA_COLUMNS: list[tuple[str, str, str]] = [
    # table, column, SQL type
    ("project_items", "parent_id", "INTEGER"),
    ("report_configs", "exec_summary", "TEXT"),
]


def run_migrations() -> None:
    """Add columns that SQLAlchemy create_all won't add to existing tables."""
    if not str(engine.url).startswith("sqlite"):
        return
    insp = inspect(engine)
    existing = {t: {c["name"] for c in insp.get_columns(t)} for t in insp.get_table_names()}
    with engine.begin() as conn:
        for table, column, sql_type in _EXTRA_COLUMNS:
            if table in existing and column not in existing[table]:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))
