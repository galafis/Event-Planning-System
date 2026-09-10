import pytest
from src.main import app, initialize_sample_data


@pytest.fixture()
def client():
    initialize_sample_data()
    return app.test_client()


@pytest.mark.parametrize(
    "data",
    [
        [],
        None,
        {},
        {"title": "X", "date": "invalid"},
        {"title": "X", "date": "2026-01-01", "budget": -1},
        {"title": "X", "date": "2026-01-01", "guest_count": 1.5},
    ],
)
def test_rejected_event_does_not_change_state(client, data):
    assert client.post("/api/events", json=data).status_code == 400
    assert len(client.get("/api/events").json) == 2


def test_update_is_atomic(client):
    before = client.get("/api/events/1").json
    assert (
        client.put("/api/events/1", json={"title": "Changed", "budget": -1}).status_code
        == 400
    )
    assert client.get("/api/events/1").json == before


def test_delete_cascades_guests(client):
    assert client.delete("/api/events/1").status_code == 200
    assert client.get("/api/guests?event_id=1").json == []
    assert client.delete("/api/events/1").status_code == 404


def test_invalid_guest_reference(client):
    assert (
        client.post(
            "/api/guests",
            json={"name": "Demo", "email": "demo@example.invalid", "event_id": 999},
        ).status_code
        == 400
    )
    assert client.get("/api/guests?event_id=abc").status_code == 400


def test_landing_page(client):
    response = client.get("/")
    assert response.status_code == 200 and b"lang=" in response.data
