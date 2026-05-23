import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set env vars for testing before importing anything
os.environ["DATABASE_URL"] = "sqlite:///./test_lexai.db"
os.environ["NVIDIA_API_KEY"] = "" # run in simulation mode

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from database.connection import Base, get_db

# Create test database engine
test_engine = create_engine("sqlite:///./test_lexai.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Clean and rebuild test tables
Base.metadata.drop_all(bind=test_engine)
Base.metadata.create_all(bind=test_engine)

# Database override dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_auth_flow():
    # 1. Register User
    reg_response = client.post(
        "/auth/register",
        json={"email": "teststudent@lexai.com", "password": "securepassword123"}
    )
    assert reg_response.status_code == 201
    assert reg_response.json()["email"] == "teststudent@lexai.com"
    
    # 2. Duplicate registration should fail
    dup_response = client.post(
        "/auth/register",
        json={"email": "teststudent@lexai.com", "password": "differentpwd"}
    )
    assert dup_response.status_code == 400

    # 3. Get JWT Token
    login_response = client.post(
        "/auth/token",
        data={"username": "teststudent@lexai.com", "password": "securepassword123"}
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    token = login_response.json()["access_token"]

    # 4. Access protected route
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "teststudent@lexai.com"

def test_ai_solver_simulation():
    # Login to get token
    login_response = client.post(
        "/auth/token",
        data={"username": "teststudent@lexai.com", "password": "securepassword123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ask a doubt solver question (simulation mode since NVIDIA_API_KEY is empty)
    chat_response = client.post(
        "/ai/chat",
        json={"message": "Explain the concept of Consideration under Indian Contract Act.", "use_rag": True},
        headers=headers
    )
    assert chat_response.status_code == 200
    assert "Simulation Mode" in chat_response.json()["response"]
    assert "sources" in chat_response.json()

if __name__ == "__main__":
    # If run directly, execute pytest on itself
    import subprocess
    print("Installing test runner dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "httpx"])
    
    import pytest
    print("\nRunning test suite...")
    sys.exit(pytest.main([__file__, "-v"]))
