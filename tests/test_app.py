import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app.activities)
    yield
    app.activities = original_activities


@pytest.fixture
def client():
    return TestClient(app.app)


def test_get_activities_returns_activity_list(client):
    # Arrange
    expected_keys = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_keys.issubset(set(data.keys()))
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "newstudent@mergington.edu"
    url = f"/activities/{activity_name}/signup?email={quote(email, safe='') }"

    # Act
    response = client.post(url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Signed up {email} for Chess Club"
    assert email in app.activities["Chess Club"]["participants"]


def test_signup_for_activity_duplicate_returns_400(client):
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/signup?email={quote(email, safe='') }"

    # Act
    response = client.post(url)
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "Student already signed up for this activity"


def test_remove_participant_deletes_existing_participant(client):
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/participants?email={quote(email, safe='') }"

    # Act
    response = client.delete(url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Removed {email} from Chess Club"
    assert email not in app.activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404(client):
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "missing@student.edu"
    url = f"/activities/{activity_name}/participants?email={quote(email, safe='') }"

    # Act
    response = client.delete(url)
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Participant not found"
