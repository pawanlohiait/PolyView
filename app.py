from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

VALID_STATUSES = {
    'active': 'Active',
    'idle': 'Idle',
    'alert': 'Alert',
    'error': 'Error',
    'unknown': 'Unknown'
}

# The central data registry holding your baseline services
SERVICES_REGISTRY = {
    'Network Monitor': {
        'status': 'Idle',
        'metrics': {'Packets Parsed': 0, 'Security Flags': 0},
        'last_seen': 'Never'
    },
    'Server Health': {
        'status': 'Idle',
        'metrics': {'CPU Core Load': '0%', 'Available VRAM': '0%'},
        'last_seen': 'Never'
    }
}

def current_timestamp() -> str:
    """Returns a clean timestamp for the frontend view."""
    return datetime.now().strftime('%H:%M:%S')

def normalize_status(status: str) -> str:
    """Cleans up messy incoming status text strings automatically."""
    if not status:
        return VALID_STATUSES['unknown']
    return VALID_STATUSES.get(str(status).strip().lower(), str(status).title())

@app.route('/')
def dashboard():
    """Renders the HTML interface template page."""
    return render_template('index.html', services=SERVICES_REGISTRY, developer_signature="UCST Student")

@app.route('/api/metrics', methods=['GET'])
def get_live_metrics():
    """Silent API route that feeds data to your HTML live auto-refresh script."""
    return jsonify(SERVICES_REGISTRY)

@app.route('/api/update', methods=['POST'])
def update_service_data():
    """Universal API Endpoint that catches and stores data from ALL your scripts."""
    payload = request.get_json()
    if not payload or 'service_name' not in payload:
        return jsonify({"error": "Invalid payload data layout."}), 400
    
    name = payload['service_name']
    raw_status = payload.get('status', 'Unknown')
    status = normalize_status(raw_status)
    metrics = payload.get('metrics', {})
    timestamp = current_timestamp()

    # Dynamically inject or update the service inside our active memory store
    SERVICES_REGISTRY[name] = {
        "status": status,
        "metrics": metrics,
        "last_seen": timestamp
    }
    return jsonify({"status": "synced", "system_mode": "production"}), 200

if __name__ == '__main__':
    print("[INIT] Booting PolyView Central Aggregator Cloud Engine...")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)