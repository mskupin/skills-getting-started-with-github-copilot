from src.app import activities


ACTIVITY_NAME = "Chess Club"
TEST_EMAIL = "student@mergington.edu"


def test_root_redirects_to_static_interface(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_participants = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert ACTIVITY_NAME in payload
    assert payload[ACTIVITY_NAME]["participants"] == expected_participants


def test_signup_adds_participant(client):
    # Arrange
    signup_url = f"/activities/{ACTIVITY_NAME}/signup"
    signup_params = {"email": TEST_EMAIL}

    # Act
    response = client.post(signup_url, params=signup_params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {TEST_EMAIL} for {ACTIVITY_NAME}"
    }
    assert TEST_EMAIL in activities[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    signup_url = f"/activities/{ACTIVITY_NAME}/signup"
    signup_params = {"email": TEST_EMAIL}
    client.post(signup_url, params=signup_params)

    # Act
    response = client.post(signup_url, params=signup_params)

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activities[ACTIVITY_NAME]["participants"].count(TEST_EMAIL) == 1


def test_signup_unknown_activity_returns_not_found(client):
    # Arrange
    signup_url = "/activities/Unknown Activity/signup"
    signup_params = {"email": TEST_EMAIL}

    # Act
    response = client.post(signup_url, params=signup_params)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    signup_url = f"/activities/{ACTIVITY_NAME}/signup"
    signup_params = {"email": TEST_EMAIL}
    client.post(signup_url, params=signup_params)
    unregister_url = f"/activities/{ACTIVITY_NAME}/participants/{TEST_EMAIL}"

    # Act
    response = client.delete(unregister_url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {TEST_EMAIL} from {ACTIVITY_NAME}"
    }
    assert TEST_EMAIL not in activities[ACTIVITY_NAME]["participants"]


def test_unregister_unknown_participant_returns_not_found(client):
    # Arrange
    unregister_url = (
        f"/activities/{ACTIVITY_NAME}/participants/"
        "not-registered@mergington.edu"
    )

    # Act
    response = client.delete(unregister_url)

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Participant not found in this activity"
    }


def test_unregister_unknown_activity_returns_not_found(client):
    # Arrange
    unregister_url = (
        "/activities/Unknown Activity/participants/"
        "student@mergington.edu"
    )

    # Act
    response = client.delete(unregister_url)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
