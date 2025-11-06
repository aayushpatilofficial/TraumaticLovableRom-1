import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'render-app-secret-key-2024'

# Minimal SocketIO config for Render
socketio = SocketIO(
    app,
    cors_allowed_origins=["*"],
    cors_credentials=False,
    ping_timeout=60,
    ping_interval=25,
    async_mode='threading'
)

connected_clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return {'status': 'ok', 'clients': len(connected_clients)}, 200

@socketio.on('connect', namespace='/')
def on_connect(auth):
    client_id = request.sid
    connected_clients[client_id] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f'✓ Client {client_id} connected. Total: {len(connected_clients)}')

    # Notify this client
    emit('connection_response', {
        'message': 'Connected to server',
        'client_id': client_id,
        'total_clients': len(connected_clients)
    })

    # Broadcast to EVERYONE using socketio.emit with broadcast=True in namespace
    socketio.emit('client_count', {'count': len(connected_clients)}, namespace='/')

@socketio.on('disconnect', namespace='/')
def on_disconnect(auth):
    client_id = request.sid
    if client_id in connected_clients:
        del connected_clients[client_id]

    print(f'✗ Client {client_id} disconnected. Total: {len(connected_clients)}')

    # Broadcast updated count
    socketio.emit('client_count', {'count': len(connected_clients)}, namespace='/')

@socketio.on('send_command', namespace='/')
def on_send_command(data, auth):
    command = data.get('command', '').strip()
    sender_id = request.sid
    timestamp = datetime.now().strftime('%H:%M:%S')

    if not command:
        print('Empty command received')
        return

    print(f'📤 Command from {sender_id}: {command}')

    # Send confirmation back to sender
    emit('command_sent', {
        'command': command,
        'timestamp': timestamp
    })

    # Send command to all OTHER clients
    socketio.emit('command_received', {
        'command': command,
        'timestamp': timestamp,
        'sender': sender_id[:6]
    }, skip_sid=sender_id, namespace='/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)