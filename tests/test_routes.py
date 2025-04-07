import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import io
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI!"}

def test_get_working():
    response = client.get("/api/working")
    assert response.status_code == 200
    assert response.json() == {"status": "working"}

@pytest.mark.asyncio
async def test_convert_resume_route():
    # Create a mock file
    file_content = b"mock pdf content"
    file = io.BytesIO(file_content)
    file.name = "test_resume.pdf"
    
    # Mock the file upload and conversion process
    with patch('app.routes.resume.convert_resume') as mock_convert:
        mock_convert.return_value = ("mock_latex", "mock_cls", {"metrics": "mock_metrics"})
        
        response = client.post(
            "/api/resume-convert",
            files={"resume_file": ("test_resume.pdf", file, "application/pdf")},
            data={"job_description": "test job description"}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-zip-compressed"
        assert "Content-Disposition" in response.headers

def test_convert_resume_route_invalid_file():
    response = client.post(
        "/api/resume-convert",
        files={"resume_file": ("test.txt", b"invalid content", "text/plain")},
        data={"job_description": "test job description"}
    )
    assert response.status_code == 500

def test_convert_resume_route_missing_job_description():
    file_content = b"mock pdf content"
    file = io.BytesIO(file_content)
    file.name = "test_resume.pdf"
    
    response = client.post(
        "/api/resume-convert",
        files={"resume_file": ("test_resume.pdf", file, "application/pdf")},
        data={}
    )
    assert response.status_code == 422  # FastAPI validation error 