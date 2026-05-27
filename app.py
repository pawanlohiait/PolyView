from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Valid standardized statuses for clean frontend UI assignment
VALID_STATUSES = {
    'active': 'Active',
    'idle': 'Idle',
    'alert': 'Alert',
    'error': 'Error',
    'unknown': 'Unknown'
}


# TEMPORARY COLD FLUSH: Wipe all cloud memory completely
SERVICES_REGISTRY = {
    'Network Monitor': {
        'status': 'Idle',
        'metrics': {'Live Packets': 0, 'Alerts Detected': 0},
        'last_seen': 'Never'
    },
    'Server Health': {
        'status': 'Idle',
        'metrics': {'CPU Usage': '0%', 'RAM Usage': '0%'},
        'last_seen': 'Never'
    }
}

def current_timestamp() -> str:
    """Returns a uniform, clean local timestamp format."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def normalize_status(status: str) -> str:
    """Standardizes incoming statuses to match our dashboard expectations."""
    if not status:
        return VALID_STATUSES['unknown']
    return VALID_STATUSES.get(str(status).strip().lower(), str(status).title())

@app.route('/')
def dashboard():
    """Renders the single-pane-of-glass dashboard UI with registered services data."""
    return render_template('index.html', services=SERVICES_REGISTRY)
@app.route('/api/flush-memory', methods=['GET'])
def flush_memory():
    """Manually clear the active dictionary metrics during the live demo."""
    global SERVICES_REGISTRY
    SERVICES_REGISTRY = {
        'Network Monitor': {
            'status': 'Idle',
            'metrics': {'Live Packets': 0, 'Alerts Detected': 0},
            'last_seen': 'Never'
        },
        'Server Health': {
            'status': 'Idle',
            'metrics': {'CPU Usage': '0%', 'RAM Usage': '0%'},
            'last_seen': 'Never'
        }
    }
    return jsonify({"message": "Memory successfully cleared back to default state!"}), 200

@app.route('/api/update', methods=['POST'])
def update_service_data():
    """
    Universal Endpoint. Any external script/service can send its data here.
    """
    payload = request.get_json()
    
    if not payload or 'service_name' not in payload:
        return jsonify({"error": "Invalid payload. 'service_name' is required."}), 400
    
    name = payload['service_name']
    raw_status = payload.get('status', 'Unknown')
    
    # Clean up the status using our normalization utilities
    status = normalize_status(raw_status)
    metrics = payload.get('metrics', {})
    timestamp = current_timestamp()

    # Dynamically register or update the service data inside the registry
    SERVICES_REGISTRY[name] = {
        "status": status,
        "metrics": metrics,
        "last_seen": timestamp
    }
    
    return jsonify({"message": f"Successfully synced data for '{name}'."}), 200

import os

if __name__ == '__main__':
    print("[SYSTEM] Booting PolyView Engine...")
    # Render assigns a dynamic port variable; fallback to 5000 for local runs
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)