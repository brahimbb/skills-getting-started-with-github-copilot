from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert {"description", "schedule", "max_participants", "participants"}.issubset(
        response.json()[expected_activity]
    )


def test_signup_adds_participant():
    # Arrange
    activity_name = "Art Club"
    email = "new.student@mergington.edu"
    activity_path = quote(activity_name, safe="")
    email_path = quote(email, safe="")

    # Act
    response = client.post(f"/activities/{activity_path}/signup?email={email_path}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_bad_request():
    # Arrange
    activity_name = "Art Club"
    email = "existing.student@mergington.edu"
    activities[activity_name]["participants"].append(email)
    activity_path = quote(activity_name, safe="")
    email_path = quote(email, safe="")

    # Act
    response = client.post(f"/activities/{activity_path}/signup?email={email_path}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activities[activity_name]["participants"].count(email) == 1


def test_signup_for_unknown_activity_returns_not_found():
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    activity_path = quote(activity_name, safe="")
    email_path = quote(email, safe="")

    # Act
    response = client.post(f"/activities/{activity_path}/signup?email={email_path}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_without_email_returns_validation_error():
    # Arrange
    activity_path = quote("Art Club", safe="")

    # Act
    response = client.post(f"/activities/{activity_path}/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Art Club"
    email = "participant@mergington.edu"
    activities[activity_name]["participants"].append(email)
    activity_path = quote(activity_name, safe="")
    email_path = quote(email, safe="")

    # Act
    response = client.delete(
        f"/activities/{activity_path}/participants/{email_path}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_unknown_activity_returns_not_found():
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    activity_path = quote(activity_name, safe="")
    email_path = quote(email, safe="")

    # Act
    response = client.delete(
        f"/activities/{activity_path}/participants/{email_path}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregistering_nonparticipant_returns_not_found():
    # Arrange
    activity_name = "Art Club"
    email = "not.registered@mergington.edu"
    activity_path = quote(activity_name, safe="")
    email_path = quote(email, safe="")

    # Act
    response = client.delete(
        f"/activities/{activity_path}/participants/{email_path}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
