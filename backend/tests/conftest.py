import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TESTS_DIR = Path(__file__).resolve().parent

# Use an isolated test database so tests never touch dev data
os.environ.setdefault("DATABASE_URL", f"sqlite:///{(TESTS_DIR / 'test_alfchamps.db').as_posix()}")

sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient

from backend.app.database import Base, SessionLocal, engine
from backend.app.main import app
from backend.app.seed import seed_all


@pytest.fixture(scope="session", autouse=True)
def _db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_all(db)
    db.commit()
    db.close()
    yield


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def project_id(client):
    resp = client.post(
        "/projects",
        json={
            "name": "Test Project",
            "standard_slugs": ["owasp-top10-web", "owasp-asvs"],
            "asvs_level": 1,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) > 0
    return data["id"]
