from src.main import app, initialize_sample_data


def run():
    initialize_sample_data()
    client = app.test_client()
    response = client.post(
        "/api/events",
        json={
            "title": "Open workshop / Oficina aberta",
            "date": "2026-10-15",
            "budget": 1500,
            "venue": "Learning lab / Laboratório didático",
        },
    )
    assert response.status_code == 201
    event_id = response.json["id"]
    task = client.post(
        f"/api/events/{event_id}/tasks",
        json={
            "title": "Prepare materials / Preparar materiais",
            "due_date": "2026-10-10",
        },
    )
    assert task.status_code == 201
    guest = client.post(
        "/api/guests",
        json={
            "name": "Example participant",
            "email": "participant@example.invalid",
            "event_id": event_id,
        },
    )
    assert guest.status_code == 201
    stats = client.get("/api/dashboard/stats").json
    return {
        "synthetic": True,
        "event_id": event_id,
        "task_id": task.json["id"],
        "guest_id": guest.json["id"],
        "total_events": stats["total_events"],
        "total_guests": stats["total_guests"],
        "total_budget": stats["total_budget"],
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), ensure_ascii=False, indent=2, allow_nan=False))
