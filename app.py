from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

quiz_questions = [
    {
        "question": "What is the capital of France?",
        "choices": ["Paris", "Berlin", "Madrid", "Rome"],
        "correct": 0
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "choices": ["Earth", "Mars", "Venus", "Jupiter"],
        "correct": 1
    },
    {
        "question": "What is the largest mammal?",
        "choices": ["Elephant", "Blue Whale", "Giraffe", "Hippopotamus"],
        "correct": 1
    }
]

current_index = 0

@app.route('/')
def screen():
    global current_index
    question = quiz_questions[current_index]
    return render_template('screen.html', question=question)
@app.route('/next')
def next_question():
    global current_index
    current_index = (current_index + 1) % len(quiz_questions)
    return redirect('/')

@app.route('/phone')
def phone():
    return render_template('phone.html')

@socketio.on('submit_answer')
def handle_answer(data):
    print("Answer from phone:", data)
    emit('new_answer', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
