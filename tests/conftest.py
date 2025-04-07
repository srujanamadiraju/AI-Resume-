import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def temp_resume_file():
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_file.write(b"mock pdf content")
        yield temp_file.name
    os.unlink(temp_file.name)

@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test_api_key") 