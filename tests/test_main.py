"""
Tests for Event Planning System API using Flask test_client.
"""

import pytest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app, events, vendors, guests, initialize_sample_data


@pytest.fixture(autouse=True)
def reset_state():
    """Reset global state before each test."""
    import src.main as m
    m.events.clear()
    m.vendors.clear()
    m.guests.clear()
    m.initialize_sample_data()
    m._next_event_id = 3
    m._next_vendor_id = 4
    m._next_guest_id = 3
    m._next_task_id = 6


@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestGetEvents:
    def test_get_events_returns_list(self, client):
        resp = client.get('/api/events')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_get_events_contains_sample_data(self, client):
        resp = client.get('/api/events')
        data = resp.get_json()
        titles = [e['title'] for e in data]
        assert 'Annual Company Gala' in titles
        assert 'Product Launch Event' in titles


class TestCreateEvent:
    def test_create_event(self, client):
        new_event = {
            'title': 'Test Event',
            'description': 'A test event',
            'date': '2025-06-01',
            'time': '10:00',
            'venue': 'Test Venue',
            'budget': 1000,
            'organizer': 'Tester'
        }
        resp = client.post('/api/events',
                           data=json.dumps(new_event),
                           content_type='application/json')
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['title'] == 'Test Event'
        assert data['id'] == 3
        assert data['status'] == 'planning'

    def test_create_event_id_no_collision(self, client):
        """Creating events after deleting should not reuse IDs."""
        # Delete event 2
        client.delete('/api/events/2')
        # Create new event
        resp = client.post('/api/events',
                           data=json.dumps({'title': 'New', 'date': '2025-01-01'}),
                           content_type='application/json')
        data = resp.get_json()
        assert data['id'] == 3  # not 2 (len-based would give 2)


class TestGetSingleEvent:
    def test_get_event_by_id(self, client):
        resp = client.get('/api/events/1')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['id'] == 1
        assert data['title'] == 'Annual Company Gala'

    def test_get_event_not_found(self, client):
        resp = client.get('/api/events/999')
        assert resp.status_code == 404


class TestUpdateEvent:
    def test_update_event(self, client):
        update = {'title': 'Updated Gala', 'budget': 60000}
        resp = client.put('/api/events/1',
                          data=json.dumps(update),
                          content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['title'] == 'Updated Gala'
        assert data['budget'] == 60000

    def test_update_event_not_found(self, client):
        resp = client.put('/api/events/999',
                          data=json.dumps({'title': 'X'}),
                          content_type='application/json')
        assert resp.status_code == 404

    def test_update_event_cannot_overwrite_id(self, client):
        """Ensure id cannot be overwritten via update."""
        resp = client.put('/api/events/1',
                          data=json.dumps({'id': 999, 'title': 'Hack'}),
                          content_type='application/json')
        data = resp.get_json()
        assert data['id'] == 1  # id unchanged

    def test_update_event_cannot_overwrite_created_at(self, client):
        """Ensure created_at cannot be overwritten via update."""
        original = client.get('/api/events/1').get_json()
        resp = client.put('/api/events/1',
                          data=json.dumps({'created_at': '1999-01-01'}),
                          content_type='application/json')
        data = resp.get_json()
        assert data['created_at'] == original['created_at']


class TestDeleteEvent:
    def test_delete_event(self, client):
        resp = client.delete('/api/events/1')
        assert resp.status_code == 200
        # Verify it's gone
        resp2 = client.get('/api/events/1')
        assert resp2.status_code == 404

    def test_delete_event_reduces_count(self, client):
        client.delete('/api/events/1')
        resp = client.get('/api/events')
        assert len(resp.get_json()) == 1


class TestDashboard:
    def test_dashboard_stats(self, client):
        resp = client.get('/api/dashboard/stats')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'total_events' in data
        assert 'upcoming_events' in data
        assert 'total_guests' in data
        assert 'confirmed_guests' in data
        assert 'total_budget' in data
        assert data['total_events'] == 2
        assert data['total_budget'] == 75000


class TestVendors:
    def test_get_vendors(self, client):
        resp = client.get('/api/vendors')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 3

    def test_create_vendor(self, client):
        resp = client.post('/api/vendors',
                           data=json.dumps({'name': 'New Vendor', 'category': 'decor'}),
                           content_type='application/json')
        assert resp.status_code == 201
        assert resp.get_json()['id'] == 4

    def test_filter_vendors_by_category(self, client):
        resp = client.get('/api/vendors?category=catering')
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'Elite Catering Services'


class TestGuests:
    def test_get_guests(self, client):
        resp = client.get('/api/guests')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2

    def test_create_guest(self, client):
        resp = client.post('/api/guests',
                           data=json.dumps({
                               'name': 'New Guest',
                               'email': 'new@test.com',
                               'event_id': 1
                           }),
                           content_type='application/json')
        assert resp.status_code == 201
        assert resp.get_json()['id'] == 3

    def test_filter_guests_by_event(self, client):
        resp = client.get('/api/guests?event_id=1')
        data = resp.get_json()
        assert len(data) == 2


class TestTasks:
    def test_add_task(self, client):
        resp = client.post('/api/events/1/tasks',
                           data=json.dumps({'title': 'New task', 'due_date': '2025-01-01'}),
                           content_type='application/json')
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['title'] == 'New task'
        assert data['completed'] is False

    def test_update_task(self, client):
        resp = client.put('/api/events/1/tasks/1',
                          data=json.dumps({'completed': True}),
                          content_type='application/json')
        assert resp.status_code == 200
        assert resp.get_json()['completed'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
