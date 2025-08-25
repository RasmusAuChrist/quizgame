from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def screen():
    return render_template('screen.html')

@app.route('/phone')
def phone():
    return render_template('phone.html')

@socketio.on('submit_answer')
def handle_answer(data):
    print("Answer from phone:", data)
    emit('new_answer', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
