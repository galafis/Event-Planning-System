from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = 'event_planning_secret_key_2024'

# In-memory storage for demo purposes
events = []
vendors = []
guests = []

# Sample data initialization
def initialize_sample_data():
    global events, vendors, guests
    
    # Sample vendors
    vendors.extend([
        {
            'id': 1,
            'name': 'Elite Catering Services',
            'category': 'catering',
            'contact': 'contact@elitecatering.com',
            'phone': '+1-555-0123',
            'rating': 4.8,
            'price_range': '$$$',
            'description': 'Premium catering services for corporate and private events'
        },
        {
            'id': 2,
            'name': 'Harmony Music Group',
            'category': 'entertainment',
            'contact': 'bookings@harmonymusic.com',
            'phone': '+1-555-0456',
            'rating': 4.6,
            'price_range': '$$',
            'description': 'Professional musicians and DJs for all types of events'
        },
        {
            'id': 3,
            'name': 'Perfect Venues',
            'category': 'venue',
            'contact': 'info@perfectvenues.com',
            'phone': '+1-555-0789',
            'rating': 4.9,
            'price_range': '$$$$',
            'description': 'Luxury event venues in prime locations'
        }
    ])
    
    # Sample events
    events.extend([
        {
            'id': 1,
            'title': 'Annual Company Gala',
            'description': 'Celebrating 10 years of excellence with employees and partners',
            'date': '2024-03-15',
            'time': '18:00',
            'venue': 'Grand Ballroom, Downtown Hotel',
            'budget': 50000,
            'guest_count': 200,
            'status': 'planning',
            'organizer': 'Sarah Johnson',
            'created_at': datetime.now().isoformat(),
            'vendors': [1, 2, 3],
            'tasks': [
                {'id': 1, 'title': 'Book venue', 'completed': True, 'due_date': '2024-01-15'},
                {'id': 2, 'title': 'Send invitations', 'completed': False, 'due_date': '2024-02-01'},
                {'id': 3, 'title': 'Finalize menu', 'completed': False, 'due_date': '2024-02-15'}
            ]
        },
        {
            'id': 2,
            'title': 'Product Launch Event',
            'description': 'Introducing our latest innovation to key stakeholders',
            'date': '2024-02-28',
            'time': '14:00',
            'venue': 'Tech Conference Center',
            'budget': 25000,
            'guest_count': 150,
            'status': 'confirmed',
            'organizer': 'Mike Chen',
            'created_at': datetime.now().isoformat(),
            'vendors': [1, 2],
            'tasks': [
                {'id': 4, 'title': 'Prepare presentation', 'completed': True, 'due_date': '2024-02-20'},
                {'id': 5, 'title': 'Setup AV equipment', 'completed': False, 'due_date': '2024-02-27'}
            ]
        }
    ])
    
    # Sample guests
    guests.extend([
        {
            'id': 1,
            'name': 'John Smith',
            'email': 'john.smith@company.com',
            'phone': '+1-555-1234',
            'event_id': 1,
            'status': 'confirmed',
            'dietary_restrictions': 'Vegetarian'
        },
        {
            'id': 2,
            'name': 'Emily Davis',
            'email': 'emily.davis@partner.com',
            'phone': '+1-555-5678',
            'event_id': 1,
            'status': 'pending',
            'dietary_restrictions': 'None'
        }
    ])

# Initialize sample data
initialize_sample_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events', methods=['GET'])
def get_events():
    return jsonify(events)

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.get_json()
    new_event = {
        'id': len(events) + 1,
        'title': data.get('title'),
        'description': data.get('description'),
        'date': data.get('date'),
        'time': data.get('time'),
        'venue': data.get('venue'),
        'budget': data.get('budget', 0),
        'guest_count': data.get('guest_count', 0),
        'status': 'planning',
        'organizer': data.get('organizer'),
        'created_at': datetime.now().isoformat(),
        'vendors': [],
        'tasks': []
    }
    events.append(new_event)
    return jsonify(new_event), 201

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = next((e for e in events if e['id'] == event_id), None)
    if event:
        return jsonify(event)
    return jsonify({'error': 'Event not found'}), 404

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    data = request.get_json()
    event.update(data)
    return jsonify(event)

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    global events
    events = [e for e in events if e['id'] != event_id]
    return jsonify({'message': 'Event deleted successfully'})

@app.route('/api/vendors', methods=['GET'])
def get_vendors():
    category = request.args.get('category')
    if category:
        filtered_vendors = [v for v in vendors if v['category'] == category]
        return jsonify(filtered_vendors)
    return jsonify(vendors)

@app.route('/api/vendors', methods=['POST'])
def create_vendor():
    data = request.get_json()
    new_vendor = {
        'id': len(vendors) + 1,
        'name': data.get('name'),
        'category': data.get('category'),
        'contact': data.get('contact'),
        'phone': data.get('phone'),
        'rating': data.get('rating', 0),
        'price_range': data.get('price_range'),
        'description': data.get('description')
    }
    vendors.append(new_vendor)
    return jsonify(new_vendor), 201

@app.route('/api/guests', methods=['GET'])
def get_guests():
    event_id = request.args.get('event_id')
    if event_id:
        filtered_guests = [g for g in guests if g['event_id'] == int(event_id)]
        return jsonify(filtered_guests)
    return jsonify(guests)

@app.route('/api/guests', methods=['POST'])
def create_guest():
    data = request.get_json()
    new_guest = {
        'id': len(guests) + 1,
        'name': data.get('name'),
        'email': data.get('email'),
        'phone': data.get('phone'),
        'event_id': data.get('event_id'),
        'status': 'pending',
        'dietary_restrictions': data.get('dietary_restrictions', 'None')
    }
    guests.append(new_guest)
    return jsonify(new_guest), 201

@app.route('/api/guests/<int:guest_id>', methods=['PUT'])
def update_guest(guest_id):
    guest = next((g for g in guests if g['id'] == guest_id), None)
    if not guest:
        return jsonify({'error': 'Guest not found'}), 404
    
    data = request.get_json()
    guest.update(data)
    return jsonify(guest)

@app.route('/api/events/<int:event_id>/tasks', methods=['POST'])
def add_task(event_id):
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    data = request.get_json()
    new_task = {
        'id': len(event.get('tasks', [])) + 1,
        'title': data.get('title'),
        'completed': False,
        'due_date': data.get('due_date')
    }
    
    if 'tasks' not in event:
        event['tasks'] = []
    event['tasks'].append(new_task)
    
    return jsonify(new_task), 201

@app.route('/api/events/<int:event_id>/tasks/<int:task_id>', methods=['PUT'])
def update_task(event_id, task_id):
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    task = next((t for t in event.get('tasks', []) if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    task.update(data)
    return jsonify(task)

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    total_events = len(events)
    upcoming_events = len([e for e in events if datetime.strptime(e['date'], '%Y-%m-%d').date() >= datetime.now().date()])
    total_guests = len(guests)
    confirmed_guests = len([g for g in guests if g['status'] == 'confirmed'])
    
    # Calculate total budget
    total_budget = sum(e.get('budget', 0) for e in events)
    
    # Recent events
    recent_events = sorted(events, key=lambda x: x['created_at'], reverse=True)[:5]
    
    # Upcoming tasks
    upcoming_tasks = []
    for event in events:
        for task in event.get('tasks', []):
            if not task['completed']:
                upcoming_tasks.append({
                    'event_title': event['title'],
                    'task_title': task['title'],
                    'due_date': task['due_date']
                })
    
    upcoming_tasks = sorted(upcoming_tasks, key=lambda x: x['due_date'])[:5]
    
    return jsonify({
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'total_guests': total_guests,
        'confirmed_guests': confirmed_guests,
        'total_budget': total_budget,
        'recent_events': recent_events,
        'upcoming_tasks': upcoming_tasks
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

