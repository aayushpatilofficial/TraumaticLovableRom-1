from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, join_room
import jwt
import time
import os

# Config
SECRET = os.environ.get('SECRET_KEY', 'supersecretkey_demo_change')
PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = SECRET
socketio = SocketIO(app, cors_allowed_origins='*')

# Whitelisted commands
WHITELIST = ['ping', 'collect_info', 'show_alert', 'open_website', 'google_search']
clients = {}  # sid -> {device_id, groups}
audit = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.get_json() or {}
    command = data.get('command')
    room = data.get('room', 'all')
    payload = data.get('payload', {})

    if command not in WHITELIST:
        return jsonify({'error': 'command not allowed'}), 400

    cmd_payload = {'command': command, 'payload': payload, 'ts': int(time.time())}
    token = jwt.encode(cmd_payload, SECRET, algorithm='HS256')

    # emit command to devices in room
    socketio.emit('command', {'command': command, 'payload': payload, 'token': token}, room=room)

    # log audit
    audit.append({'command': command, 'room': room, 'payload': payload, 'ts': time.time()})
    return jsonify({'ok': True, 'issued': cmd_payload})

@app.route('/audit')
def get_audit():
    return jsonify(audit[-200:])

# SocketIO events
@socketio.on('connect')
def on_connect():
    print('Client connected:', request.sid)

@socketio.on('register')
def on_register(data):
    device_id = data.get('device_id')
    groups = data.get('groups', [])
    clients[request.sid] = {'device_id': device_id, 'groups': groups}
    for g in groups:
        join_room(g)
    print(f'Device registered: {device_id}, groups={groups}')

@socketio.on('command_result')
def on_result(data):
    print('Result from device:', data)
    audit.append({'result': data, 'ts': time.time()})

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected:', request.sid)
    clients.pop(request.sid, None)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=PORT)