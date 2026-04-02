import pytest
import json
import os

from app import app, init_db


@pytest.fixture
def client(tmp_path):
    # use a real file-based db per test so all requests share the same db
    test_db = str(tmp_path / "test.db")
    os.environ["DB_PATH"] = test_db
    app.config["TESTING"] = True
    with app.test_client() as c:
        init_db()
        yield c
    os.environ.pop("DB_PATH", None)


# ---------- home ----------

def test_home_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_home_contains_program_names(client):
    resp = client.get("/")
    body = resp.data.decode()
    assert "Fat Loss" in body
    assert "Muscle Gain" in body
    assert "Beginner" in body


# ---------- programs ----------

def test_list_programs(client):
    resp = client.get("/api/programs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 3
    names = [p["name"] for p in data]
    assert "Fat Loss (FL)" in names
    assert "Muscle Gain (MG)" in names
    assert "Beginner (BG)" in names


def test_get_program_fat_loss(client):
    resp = client.get("/api/programs/Fat Loss (FL)")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Fat Loss (FL)"
    assert "workout" in data
    assert "diet" in data
    assert data["calorie_factor"] == 22


def test_get_program_muscle_gain(client):
    resp = client.get("/api/programs/Muscle Gain (MG)")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["calorie_factor"] == 35


def test_get_program_beginner(client):
    resp = client.get("/api/programs/Beginner (BG)")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["calorie_factor"] == 26


def test_get_program_not_found(client):
    resp = client.get("/api/programs/SomeRandomProgram")
    assert resp.status_code == 404


# ---------- calorie calculator ----------

def test_calorie_calculation_fat_loss(client):
    payload = {"weight": 70, "program": "Fat Loss (FL)"}
    resp = client.post(
        "/api/calculate-calories",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    # 70 * 22 = 1540
    assert data["calories"] == 1540


def test_calorie_calculation_muscle_gain(client):
    payload = {"weight": 80, "program": "Muscle Gain (MG)"}
    resp = client.post(
        "/api/calculate-calories",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    # 80 * 35 = 2800
    assert data["calories"] == 2800


def test_calorie_calculation_missing_fields(client):
    resp = client.post(
        "/api/calculate-calories",
        data=json.dumps({"weight": 70}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_calorie_calculation_invalid_program(client):
    payload = {"weight": 70, "program": "NonExistent"}
    resp = client.post(
        "/api/calculate-calories",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_calorie_calculation_zero_weight(client):
    payload = {"weight": 0, "program": "Fat Loss (FL)"}
    resp = client.post(
        "/api/calculate-calories",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_calorie_calculation_negative_weight(client):
    payload = {"weight": -10, "program": "Fat Loss (FL)"}
    resp = client.post(
        "/api/calculate-calories",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400


# ---------- clients ----------

def test_create_client(client):
    payload = {
        "name": "Arun Kumar",
        "age": 28,
        "weight": 72,
        "program": "Muscle Gain (MG)",
    }
    resp = client.post(
        "/api/clients",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Arun Kumar"


def test_create_client_missing_name(client):
    payload = {"age": 25, "weight": 65, "program": "Fat Loss (FL)"}
    resp = client.post(
        "/api/clients",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_create_client_invalid_program(client):
    payload = {"name": "Test User", "program": "Fake Program"}
    resp = client.post(
        "/api/clients",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_get_client(client):
    # create first
    payload = {"name": "Priya S", "age": 30, "weight": 60, "program": "Fat Loss (FL)"}
    client.post(
        "/api/clients",
        data=json.dumps(payload),
        content_type="application/json",
    )
    # then fetch
    resp = client.get("/api/clients/Priya S")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Priya S"
    assert data["program"] == "Fat Loss (FL)"


def test_get_client_not_found(client):
    resp = client.get("/api/clients/NoSuchPerson")
    assert resp.status_code == 404


def test_list_clients_empty(client):
    resp = client.get("/api/clients")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_list_clients_after_insert(client):
    client.post(
        "/api/clients",
        data=json.dumps({"name": "Raj M", "program": "Beginner (BG)"}),
        content_type="application/json",
    )
    resp = client.get("/api/clients")
    data = resp.get_json()
    assert len(data) >= 1
    assert any(c["name"] == "Raj M" for c in data)
