import pytest
from fastapi.testclient import TestClient

from home_budget.main import app

client = TestClient(app)

base_url = "/api/v1/categories"

username = "testuser"
password = "testpass"


def get_token():
    client.post("/api/v1/users/register", json={"username": username, "password": password})
    response = client.post("/api/v1/users/login", data={"username": username, "password": password})
    return response.json().get("access_token")


def auth_headers():
    token = get_token()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module", autouse=True)
def cleanup_user():
    yield
    client.delete(f"/api/v1/users/{username}")


def create_category(name="Test Category"):
    response = client.post(base_url + "/create", json={"name": name}, headers=auth_headers())
    return response


def delete_category(category_id):
    response = client.delete(f"{base_url}/delete/{category_id}", headers=auth_headers())
    return response


def test_create_category():
    response = create_category()
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"
    delete_category(data["id"])


def test_create_duplicate_category():
    response1 = create_category("Duplicate Cat")
    assert response1.status_code == 200

    response2 = create_category("Duplicate Cat")
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Category already exists"

    delete_category(response1.json()["id"])


def test_get_all_categories():
    create_response = create_category("List Cat")
    assert create_response.status_code == 200

    response = client.get(base_url + "/getAll", headers=auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert any(cat["name"] == "List Cat" for cat in data)

    delete_category(create_response.json()["id"])


def test_update_category():
    create_response = create_category("Old Name")
    cat_id = create_response.json()["id"]

    update_response = client.put(
        f"{base_url}/update/{cat_id}",
        json={"name": "New Name"},
        headers=auth_headers()
    )
    assert update_response.status_code == 200
    updated_cat = update_response.json()
    assert updated_cat["name"] == "New Name"

    delete_category(cat_id)


def test_delete_category():
    create_response = create_category("Delete Me")
    cat_id = create_response.json()["id"]

    delete_response = delete_category(cat_id)
    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Category deleted successfully"

    delete_again = delete_category(cat_id)
    assert delete_again.status_code == 404
