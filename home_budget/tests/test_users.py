from fastapi.testclient import TestClient

from home_budget.main import app

client = TestClient(app)

base_url = "/api/v1/users"
username = "testuser"
password = "testpass"


def delete_user():
    response = client.delete(f"{base_url}/{username}")
    return response


def test_register_user():
    response = client.post(base_url + "/register", json={
        "username": username,
        "password": password
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == username

    delete_user()


def test_login_user():
    client.post(base_url + "/register", json={
        "username": username,
        "password": password
    })
    response = client.post(base_url + "/login", data={
        "username": username,
        "password": password
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

    delete_user()


def test_register_duplicate_user():
    client.post(base_url + "/register", json={
        "username": username,
        "password": password
    })
    response = client.post(base_url + "/register", json={
        "username": username,
        "password": "newpassword"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"
    delete_user()


def test_login_invalid_credentials():
    response = client.post(base_url + "/login", data={
        "username": "notreal",
        "password": "wrong"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
