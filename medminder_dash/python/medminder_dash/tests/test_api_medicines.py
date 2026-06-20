import json

import pytest
from medminder_dash.app import create_app
from medminder_dash.medicines_state import Medicine


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        from medminder_dash.app import store
        store._medicines.clear()
        store._lock = __import__("threading").Lock()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded_store(app):
    from medminder_dash.app import store
    m1 = Medicine(name="Ibup", hour=8, minute=30, day_of_week=1, day_of_month=0)
    store.add(m1)
    store.add(Medicine(name="PaRa", hour=20, minute=0, day_of_week=3, day_of_month=0))
    return m1


class TestApiMedicinesList:
    def test_list_empty(self, client):
        resp = client.get("/api/medicines")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_with_medicines(self, client, seeded_store):
        resp = client.get("/api/medicines")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2
        names = [m["name"] for m in data]
        assert "Ibup" in names
        assert "PaRa" in names


class TestApiMedicineCreate:
    def test_create_valid(self, client):
        resp = client.post(
            "/api/medicine",
            data=json.dumps({"name": "Aspirin", "hour": 8, "minute": 0}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Aspirin"
        assert data["hour"] == 8
        assert data["minute"] == 0
        assert data["enabled"] is True

    def test_create_missing_body(self, client):
        resp = client.post(
            "/api/medicine",
            data="not-json",
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_create_invalid_data(self, client):
        resp = client.post(
            "/api/medicine",
            data=json.dumps({"name": "", "hour": 25, "minute": 15}),
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data


class TestApiMedicineGet:
    def test_get_existing(self, client, seeded_store):
        med_id = seeded_store.id
        resp = client.get(f"/api/medicine/{med_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Ibup"

    def test_get_not_found(self, client):
        resp = client.get("/api/medicine/nonexistent")
        assert resp.status_code == 404
        assert resp.get_json()["error"] == "Not found"


class TestApiMedicineUpdate:
    def test_update_valid(self, client, seeded_store):
        med_id = seeded_store.id
        resp = client.put(
            f"/api/medicine/{med_id}",
            data=json.dumps({"name": "Ibup", "hour": 9, "minute": 0}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["hour"] == 9

    def test_update_missing_body(self, client, seeded_store):
        med_id = seeded_store.id
        resp = client.put(
            f"/api/medicine/{med_id}",
            data="not-json",
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_update_not_found(self, client):
        resp = client.put(
            "/api/medicine/nonexistent",
            data=json.dumps({"name": "x", "hour": 1, "minute": 0}),
            content_type="application/json",
        )
        assert resp.status_code == 404


class TestApiMedicineDelete:
    def test_delete_existing(self, client, seeded_store):
        med_id = seeded_store.id
        resp = client.delete(f"/api/medicine/{med_id}")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "deleted"}

    def test_delete_not_found(self, client):
        resp = client.delete("/api/medicine/nonexistent")
        assert resp.status_code == 404
        assert resp.get_json()["error"] == "Not found"


class TestApiMedicineToggle:
    def test_toggle_existing(self, client, seeded_store):
        med_id = seeded_store.id
        assert seeded_store.enabled is True
        resp = client.put(f"/api/medicine/{med_id}/toggle")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["enabled"] is False

    def test_toggle_not_found(self, client):
        resp = client.put("/api/medicine/nonexistent/toggle")
        assert resp.status_code == 404
        assert resp.get_json()["error"] == "Not found"
