from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import webbrowser

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

last_command = ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    global last_command
    data = request.json
    command = data.get("command")
    last_command = command
    socketio.emit("command_received", {"command": command})
    return jsonify({"status": "Command broadcasted", "command": command})

@socketio.on('connect')
def handle_connect():
    if last_command:
        emit("command_received", {"command": last_command})

@socketio.on('execute_local')
def handle_execute_local(data):
    command = data.get("command")
    if command.startswith("open "):
        url = command.replace("open ", "")
        if not url.startswith("http"):
            url = "https://" + url
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening {url}: {e}")
    emit("done", {"status": "executed"})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
