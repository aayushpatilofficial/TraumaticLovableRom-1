from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# handle command sending
@socketio.on('send_command')
def handle_command(data):
    cmd = data.get('cmd')
    # broadcast to all devices including sender
    emit('broadcast_command', {'cmd': cmd}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
