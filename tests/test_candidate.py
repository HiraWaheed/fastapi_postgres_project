import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup for a test database
SQLALCHEMY_DATABASE_URL = (
    "sqlite:///./test.db"  # Adjust path as needed for your test environment
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency for tests
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)  # Create tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)  # Drop tables after tests


@pytest.fixture(scope="module")
def client(test_db):
    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_user(client):
    response = client.post(
        "/user", json={"username": "Verynewuser1", "password": "Verynewpass1"}
    )
    return response.json()


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/login", data={"username": "Verynewuser1", "password": "Verynewpass1"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_add_candidate(client, auth_headers):
    candidate_data = {
        "first_name": "John",
        "last_name": "Doe",
        "experience": 5,
    }
    response = client.post("/candidates", json=candidate_data, headers=auth_headers)
    assert response.status_code == 200
    assert "id" in response.json()


def test_fetch_candidate(client, auth_headers, test_db):
    candidate_data = {
        "first_name": "Janeeeee",
        "last_name": "Doe",
        "experience": 3,
    }
    response = client.post("/candidates", json=candidate_data, headers=auth_headers)
    candidate_id = response.json()["id"]

    response = client.get(f"/candidates/{candidate_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Janeeeee"
    assert response.json()["experience"] == 3


def test_update_candidate(client, auth_headers, test_db):
    candidate_data = {
        "first_name": "Update",
        "last_name": "Candidate",
        "experience": 4,
    }
    response = client.post("/candidates", json=candidate_data, headers=auth_headers)
    candidate_id = response.json()["id"]

    updated_data = {
        "first_name": "Updated",
        "last_name": "Candidate",
        "experience": 6,
    }
    response = client.put(
        f"/candidates/{candidate_id}", json=updated_data, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"
    assert response.json()["experience"] == 6


def test_delete_candidate(client, auth_headers, test_db):
    candidate_data = {
        "first_name": "ToBeDeleted",
        "last_name": "Candidate",
        "experience": 2,
    }
    response = client.post("/candidates", json=candidate_data, headers=auth_headers)
    candidate_id = response.json()["id"]

    response = client.delete(f"/candidates/{candidate_id}", headers=auth_headers)
    assert response.status_code == 200


def test_fetch_all_candidates(client, auth_headers):
    candidates_data = [
        {"first_name": "Alice", "last_name": "Smith", "experience": 1},
        {"first_name": "Bob", "last_name": "Johnson", "experience": 2},
        {"first_name": "Charlie", "last_name": "Brown", "experience": 3},
    ]
    for candidate_data in candidates_data:
        client.post("/candidates", json=candidate_data, headers=auth_headers)

    response = client.get("/all-candidates?page=1&page_size=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_candidates" in data
    assert "candidates" in data
    assert len(data["candidates"]) <= 2  # Page size limit
