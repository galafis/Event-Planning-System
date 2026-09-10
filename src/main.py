from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import json
import os
import math
from threading import RLock
from flask import g
from werkzeug.exceptions import BadRequest

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
app.config["MAX_CONTENT_LENGTH"] = 100000
_state_lock = RLock()


@app.before_request
def validate_request():
    _state_lock.acquire()
    g.state_locked = True
    if request.method not in {"POST", "PUT"} or not request.path.startswith("/api/"):
        return None
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BadRequest("JSON object required / objeto JSON obrigatório")
    create = request.method == "POST"
    path = request.path
    required = []
    if create:
        if path == "/api/events":
            required = ["title", "date"]
        elif path == "/api/vendors":
            required = ["name", "category"]
        elif path == "/api/guests":
            required = ["name", "email", "event_id"]
        elif path.endswith("/tasks"):
            required = ["title", "due_date"]
    if any(key not in data for key in required):
        raise BadRequest("Required fields missing / campos obrigatórios ausentes")
    for key in (
        "title",
        "name",
        "email",
        "category",
        "organizer",
        "description",
        "venue",
        "phone",
        "contact",
        "dietary_restrictions",
        "price_range",
    ):
        if key in data and (
            not isinstance(data[key], str)
            or not data[key].strip()
            or len(data[key]) > 2000
        ):
            raise BadRequest(f"Invalid {key} / campo inválido")
    for key in ("date", "due_date"):
        if key in data:
            try:
                if not isinstance(data[key], str) or len(data[key]) != 10:
                    raise ValueError()
                datetime.strptime(data[key], "%Y-%m-%d")
            except (TypeError, ValueError):
                raise BadRequest(f"{key}: YYYY-MM-DD required / data inválida")
    if "time" in data:
        try:
            datetime.strptime(data["time"], "%H:%M")
        except (ValueError, TypeError):
            raise BadRequest("Invalid time / horário inválido")
    for key in ("budget", "guest_count", "rating"):
        if key in data:
            value = data[key]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not 0 <= value <= 1e12
            ):
                raise BadRequest(f"Invalid {key} / valor inválido")
            if key == "guest_count" and not isinstance(value, int):
                raise BadRequest("Integer guest count required / quantidade inteira")
            if key == "rating" and value > 5:
                raise BadRequest("Rating must be 0–5 / avaliação de 0 a 5")
    if "completed" in data and not isinstance(data["completed"], bool):
        raise BadRequest("Boolean completed required / conclusão booleana")
    if "event_id" in data:
        value = data["event_id"]
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not any(e["id"] == value for e in events)
        ):
            raise BadRequest("Unknown event / evento desconhecido")
    if "status" in data:
        allowed = (
            {"planning", "confirmed", "completed", "cancelled"}
            if "/events/" in path
            else {"pending", "confirmed", "declined"}
        )
        if not isinstance(data["status"], str) or data["status"] not in allowed:
            raise BadRequest("Invalid status / status inválido")


@app.teardown_request
def release_state_lock(error=None):
    if g.pop("state_locked", False):
        _state_lock.release()


@app.errorhandler(BadRequest)
def invalid_request(error):
    return jsonify({"error": error.description}), 400


# In-memory storage for demo purposes
events = []
vendors = []
guests = []

# Module-level ID counters (initialized after sample data)
_next_event_id = 3
_next_vendor_id = 4
_next_guest_id = 3
_next_task_id = 6


# Sample data initialization
def initialize_sample_data():
    global \
        events, \
        vendors, \
        guests, \
        _next_event_id, \
        _next_vendor_id, \
        _next_guest_id, \
        _next_task_id
    events.clear()
    vendors.clear()
    guests.clear()
    _next_event_id, _next_vendor_id, _next_guest_id, _next_task_id = 3, 4, 3, 6

    # Sample vendors
    vendors.extend(
        [
            {
                "id": 1,
                "name": "Elite Catering Services",
                "category": "catering",
                "contact": "contact@example.invalid",
                "phone": "+1-555-0123",
                "rating": 4.8,
                "price_range": "$$$",
                "description": "Premium catering services for corporate and private events",
            },
            {
                "id": 2,
                "name": "Harmony Music Group",
                "category": "entertainment",
                "contact": "bookings@example.invalid",
                "phone": "+1-555-0456",
                "rating": 4.6,
                "price_range": "$$",
                "description": "Professional musicians and DJs for all types of events",
            },
            {
                "id": 3,
                "name": "Perfect Venues",
                "category": "venue",
                "contact": "info@example.invalid",
                "phone": "+1-555-0789",
                "rating": 4.9,
                "price_range": "$$$$",
                "description": "Luxury event venues in prime locations",
            },
        ]
    )

    # Sample events
    events.extend(
        [
            {
                "id": 1,
                "title": "Annual Company Gala",
                "description": "Celebrating 10 years of excellence with employees and partners",
                "date": "2024-03-15",
                "time": "18:00",
                "venue": "Grand Ballroom, Downtown Hotel",
                "budget": 50000,
                "guest_count": 200,
                "status": "planning",
                "organizer": "Sarah Johnson",
                "created_at": datetime.now().isoformat(),
                "vendors": [1, 2, 3],
                "tasks": [
                    {
                        "id": 1,
                        "title": "Book venue",
                        "completed": True,
                        "due_date": "2024-01-15",
                    },
                    {
                        "id": 2,
                        "title": "Send invitations",
                        "completed": False,
                        "due_date": "2024-02-01",
                    },
                    {
                        "id": 3,
                        "title": "Finalize menu",
                        "completed": False,
                        "due_date": "2024-02-15",
                    },
                ],
            },
            {
                "id": 2,
                "title": "Product Launch Event",
                "description": "Introducing our latest innovation to key stakeholders",
                "date": "2024-02-28",
                "time": "14:00",
                "venue": "Tech Conference Center",
                "budget": 25000,
                "guest_count": 150,
                "status": "confirmed",
                "organizer": "Mike Chen",
                "created_at": datetime.now().isoformat(),
                "vendors": [1, 2],
                "tasks": [
                    {
                        "id": 4,
                        "title": "Prepare presentation",
                        "completed": True,
                        "due_date": "2024-02-20",
                    },
                    {
                        "id": 5,
                        "title": "Setup AV equipment",
                        "completed": False,
                        "due_date": "2024-02-27",
                    },
                ],
            },
        ]
    )

    # Sample guests
    guests.extend(
        [
            {
                "id": 1,
                "name": "John Smith",
                "email": "john.smith@example.invalid",
                "phone": "+1-555-1234",
                "event_id": 1,
                "status": "confirmed",
                "dietary_restrictions": "Vegetarian",
            },
            {
                "id": 2,
                "name": "Emily Davis",
                "email": "emily.davis@example.invalid",
                "phone": "+1-555-5678",
                "event_id": 1,
                "status": "pending",
                "dietary_restrictions": "None",
            },
        ]
    )


# Initialize sample data
initialize_sample_data()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/events", methods=["GET"])
def get_events():
    return jsonify(events)


@app.route("/api/events", methods=["POST"])
def create_event():
    global _next_event_id
    data = request.get_json()
    new_event = {
        "id": _next_event_id,
        "title": data.get("title"),
        "description": data.get("description"),
        "date": data.get("date"),
        "time": data.get("time"),
        "venue": data.get("venue"),
        "budget": data.get("budget", 0),
        "guest_count": data.get("guest_count", 0),
        "status": "planning",
        "organizer": data.get("organizer"),
        "created_at": datetime.now().isoformat(),
        "vendors": [],
        "tasks": [],
    }
    _next_event_id += 1
    events.append(new_event)
    return jsonify(new_event), 201


@app.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    event = next((e for e in events if e["id"] == event_id), None)
    if event:
        return jsonify(event)
    return jsonify({"error": "Event not found"}), 404


@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    data = request.get_json()
    allowed_fields = {
        "title",
        "description",
        "date",
        "time",
        "venue",
        "budget",
        "guest_count",
        "status",
        "organizer",
    }
    for key in allowed_fields:
        if key in data:
            event[key] = data[key]
    return jsonify(event)


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    global events
    if not any(e["id"] == event_id for e in events):
        return jsonify({"error": "Event not found / evento não encontrado"}), 404
    events[:] = [e for e in events if e["id"] != event_id]
    guests[:] = [g for g in guests if g["event_id"] != event_id]
    return jsonify({"message": "Event deleted successfully"})


@app.route("/api/vendors", methods=["GET"])
def get_vendors():
    category = request.args.get("category")
    if category:
        filtered_vendors = [v for v in vendors if v["category"] == category]
        return jsonify(filtered_vendors)
    return jsonify(vendors)


@app.route("/api/vendors", methods=["POST"])
def create_vendor():
    global _next_vendor_id
    data = request.get_json()
    new_vendor = {
        "id": _next_vendor_id,
        "name": data.get("name"),
        "category": data.get("category"),
        "contact": data.get("contact"),
        "phone": data.get("phone"),
        "rating": data.get("rating", 0),
        "price_range": data.get("price_range"),
        "description": data.get("description"),
    }
    _next_vendor_id += 1
    vendors.append(new_vendor)
    return jsonify(new_vendor), 201


@app.route("/api/guests", methods=["GET"])
def get_guests():
    event_id = request.args.get("event_id")
    if event_id:
        try:
            event_id = int(event_id)
        except ValueError:
            raise BadRequest("Invalid event_id / identificador inválido")
        filtered_guests = [g for g in guests if g["event_id"] == event_id]
        return jsonify(filtered_guests)
    return jsonify(guests)


@app.route("/api/guests", methods=["POST"])
def create_guest():
    global _next_guest_id
    data = request.get_json()
    new_guest = {
        "id": _next_guest_id,
        "name": data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "event_id": data.get("event_id"),
        "status": "pending",
        "dietary_restrictions": data.get("dietary_restrictions", "None"),
    }
    _next_guest_id += 1
    guests.append(new_guest)
    return jsonify(new_guest), 201


@app.route("/api/guests/<int:guest_id>", methods=["PUT"])
def update_guest(guest_id):
    guest = next((g for g in guests if g["id"] == guest_id), None)
    if not guest:
        return jsonify({"error": "Guest not found"}), 404

    data = request.get_json()
    allowed_fields = {
        "name",
        "email",
        "phone",
        "event_id",
        "status",
        "dietary_restrictions",
    }
    for key in allowed_fields:
        if key in data:
            guest[key] = data[key]
    return jsonify(guest)


@app.route("/api/events/<int:event_id>/tasks", methods=["POST"])
def add_task(event_id):
    global _next_task_id
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    data = request.get_json()
    new_task = {
        "id": _next_task_id,
        "title": data.get("title"),
        "completed": False,
        "due_date": data.get("due_date"),
    }
    _next_task_id += 1

    if "tasks" not in event:
        event["tasks"] = []
    event["tasks"].append(new_task)

    return jsonify(new_task), 201


@app.route("/api/events/<int:event_id>/tasks/<int:task_id>", methods=["PUT"])
def update_task(event_id, task_id):
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    task = next((t for t in event.get("tasks", []) if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    allowed_fields = {"title", "completed", "due_date"}
    for key in allowed_fields:
        if key in data:
            task[key] = data[key]
    return jsonify(task)


@app.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    total_events = len(events)
    upcoming_events = len(
        [
            e
            for e in events
            if datetime.strptime(e["date"], "%Y-%m-%d").date() >= datetime.now().date()
        ]
    )
    total_guests = len(guests)
    confirmed_guests = len([g for g in guests if g["status"] == "confirmed"])

    # Calculate total budget
    total_budget = sum(e.get("budget", 0) for e in events)

    # Recent events
    recent_events = sorted(events, key=lambda x: x["created_at"], reverse=True)[:5]

    # Upcoming tasks
    upcoming_tasks = []
    for event in events:
        for task in event.get("tasks", []):
            if not task["completed"]:
                upcoming_tasks.append(
                    {
                        "event_title": event["title"],
                        "task_title": task["title"],
                        "due_date": task["due_date"],
                    }
                )

    upcoming_tasks = sorted(upcoming_tasks, key=lambda x: x["due_date"])[:5]

    return jsonify(
        {
            "total_events": total_events,
            "upcoming_events": upcoming_events,
            "total_guests": total_guests,
            "confirmed_guests": confirmed_guests,
            "total_budget": total_budget,
            "recent_events": recent_events,
            "upcoming_tasks": upcoming_tasks,
        }
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
