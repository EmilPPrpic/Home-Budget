import pytest
from fastapi.testclient import TestClient

from home_budget.main import app

client = TestClient(app)

base_url = "/api/v1/expenses"
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


def create_category_for_expenses():
    cat_response = client.post(
        "/api/v1/categories/create",
        json={"name": "TestCategory"},
        headers=auth_headers()
    )
    return cat_response.json()


def delete_category(category_id: int):
    client.delete(f"/api/v1/categories/delete/{category_id}", headers=auth_headers())


def test_create_expense():
    category = create_category_for_expenses()
    category_id = category["id"]

    response = client.post(
        base_url + "/create",
        json={
            "name": "Test Expense",
            "amount": 100.0,
            "date": "2025-01-01",
            "category_id": category_id
        },
        headers=auth_headers()
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Expense"
    assert data["amount"] == 100.0

    expense_id = data["id"]
    client.delete(f"{base_url}/delete/{expense_id}", headers=auth_headers())
    delete_category(category_id)


def test_get_all_expenses_empty():
    response = client.get(base_url + "/getAll", headers=auth_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_expenses_by_category():
    category = create_category_for_expenses()
    category_id = category["id"]

    client.post(
        base_url + "/create",
        json={
            "name": "Category Expense",
            "amount": 50,
            "date": "2025-01-01",
            "category_id": category_id
        },
        headers=auth_headers()
    )

    response = client.get(f"{base_url}/getByCategory/{category_id}", headers=auth_headers())
    assert response.status_code == 200
    expenses = response.json()
    assert isinstance(expenses, list)
    assert any(exp["category_id"] == category_id for exp in expenses)

    for expense in expenses:
        client.delete(f"{base_url}/delete/{expense['id']}", headers=auth_headers())
    delete_category(category_id)


def test_update_expense():
    category = create_category_for_expenses()
    category_id = category["id"]

    create_resp = client.post(
        base_url + "/create",
        json={
            "name": "ToUpdate",
            "amount": 20,
            "date": "2025-01-01",
            "category_id": category_id
        },
        headers=auth_headers()
    )
    expense_id = create_resp.json()["id"]

    update_resp = client.put(
        f"{base_url}/update/{expense_id}",
        json={"amount": 40, "name": "Updated Name"},
        headers=auth_headers()
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["amount"] == 40
    assert updated["name"] == "Updated Name"

    client.delete(f"{base_url}/delete/{expense_id}", headers=auth_headers())
    delete_category(category_id)


def test_delete_expense():
    category = create_category_for_expenses()
    category_id = category["id"]

    create_resp = client.post(
        base_url + "/create",
        json={
            "name": "ToDelete",
            "amount": 10,
            "date": "2025-01-01",
            "category_id": category_id
        },
        headers=auth_headers()
    )
    expense_id = create_resp.json()["id"]

    del_resp = client.delete(f"{base_url}/delete/{expense_id}", headers=auth_headers())
    assert del_resp.status_code == 200
    assert del_resp.json()["detail"] == "Expense deleted successfully"

    delete_category(category_id)


def test_expense_summary():
    category = create_category_for_expenses()
    category_id = category["id"]

    client.post(
        base_url + "/create",
        json={
            "name": "Sum1",
            "amount": 30,
            "date": "2025-01-01",
            "category_id": category_id
        },
        headers=auth_headers()
    )
    client.post(
        base_url + "/create",
        json={
            "name": "Sum2",
            "amount": 70,
            "date": "2025-01-02",
            "category_id": category_id
        },
        headers=auth_headers()
    )

    response = client.get(
        base_url + "/summary",
        headers=auth_headers(),
        params={"start_date": "2025-01-01", "end_date": "2025-01-05"}
    )
    assert response.status_code == 200
    summary = response.json()
    assert "total_expenses" in summary
    assert summary["total_expenses"] == 100.0
    assert isinstance(summary["category_performance"], list)

    expenses = client.get(base_url + "/getAll", headers=auth_headers()).json()
    for exp in expenses:
        client.delete(f"{base_url}/delete/{exp['id']}", headers=auth_headers())
    delete_category(category_id)
