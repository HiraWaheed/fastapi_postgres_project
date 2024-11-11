import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.database import SessionLocal
from app.utils.helper import hash_password

client = TestClient(app)


@pytest.fixture(scope="module")
def db_session():
    # Creating a new session for each test
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def create_user(db_session):
    user_data = {"username": "testuser", "password": "testpassword"}
    hashed_password = hash_password(user_data["password"])
    new_user = User(username=user_data["username"], password=hashed_password)
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return new_user


# Test for registering a new user
def test_register_user(db_session):
    user_data = {"username": "newuser9", "password": "newpassword"}
    response = client.post("/user", json=user_data)

    assert response.status_code == 200
    assert "username" in response.json()
    assert response.json()["username"] == "newuser9"


# Test for user registration with existing username
def test_register_user_username_exists(db_session, create_user):
    existing_user_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/user", json=existing_user_data)

    assert response.status_code == 400
    assert (
        "Username already exists. Please enter a different username"
        in response.json()["detail"]
    )


# Test for successful login
def test_login_success(create_user):
    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/login", data=login_data)

    assert response.status_code == 200
    assert "access_token" in response.json()


# Test for invalid login
def test_login_invalid_credentials(db_session):
    login_data = {"username": "newuser3", "password": "password"}
    response = client.post("/login", data=login_data)

    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]
