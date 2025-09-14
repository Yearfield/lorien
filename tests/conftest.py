import os
import tempfile
import shutil
import pytest
from fastapi.testclient import TestClient
from api.db.migrate import apply_migrations

@pytest.fixture(scope="session")
def _test_db():
    """Create a temporary database for testing using migrations"""
    d = tempfile.mkdtemp(prefix="lorien_testdb_")
    path = os.path.join(d, "app.db")
    os.environ["LORIEN_DB_PATH"] = path
    apply_migrations(path)
    yield path
    shutil.rmtree(d, ignore_errors=True)

@pytest.fixture
def client(_test_db):
    """FastAPI test client"""
    # Import app after setting the environment variable
    from api.main import app
    return TestClient(app)