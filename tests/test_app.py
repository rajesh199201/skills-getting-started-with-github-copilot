import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Helper: get a unique email for tests
def unique_email(base="testuser"):
    import uuid
    return f"{base}-{uuid.uuid4().hex[:8]}@mergington.edu"

def test_get_activities():
    # Arrange
    # (client is ready)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_success():
    # Arrange
    email = unique_email()
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]
    # Confirm participant is added
    participants = client.get("/activities").json()[activity]["participants"]
    assert email in participants

def test_signup_duplicate():
    # Arrange
    email = unique_email()
    activity = "Programming Class"
    # Act
    first = client.post(f"/activities/{activity}/signup", params={"email": email})
    second = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert first.status_code == 200
    assert second.status_code == 400
    assert "already signed up" in second.json()["detail"].lower()

def test_unregister_success():
    # Arrange
    email = unique_email()
    activity = "Gym Class"
    client.post(f"/activities/{activity}/signup", params={"email": email})
    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    # Confirm participant is removed
    participants = client.get("/activities").json()[activity]["participants"]
    assert email not in participants

def test_unregister_not_found():
    # Arrange
    email = unique_email()
    activity = "Math Olympiad"
    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
