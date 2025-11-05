from flask import Flask, render_template, request
from flask_socketio import SocketIO
import subprocess
import webbrowser
import os
import sys

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('execute_command')
def handle_command(data):
    cmd = data.get('command')
    result = ""

    try:
        # Open websites
        if cmd.startswith("open "):
            url = cmd[5:]
            if not url.startswith("http"):
                url = "https://" + url
            webbrowser.open(url)
            result = f"Opened {url}"
        else:
            # Execute system command
            completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            result = completed.stdout if completed.stdout else completed.stderr
    except Exception as e:
        result = str(e)

    # Send result back to client
    socketio.emit('command_result', {'result': result})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
