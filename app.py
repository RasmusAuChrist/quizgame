from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import random, json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load all questions from file
with open("questions.json", "r") as f:
    all_questions = json.load(f)

game_state = {
    "player": None,
    "questions": [],
    "current_index": 0
}

@app.route('/')
def screen():
    return render_template('screen.html')

@app.route('/phone')
def phone():
    return render_template('phone.html')

@socketio.on('player_joined')
def handle_player_joined(data):
    print(f"Player joined: {data['name']}")
    game_state["player"] = data['name']
    game_state["questions"] = random.sample(all_questions, 10)
    game_state["current_index"] = 0

    emit("player_joined", {"name": data['name']}, broadcast=True)
    emit("show_question", {
        "index": 0,
        "question": game_state["questions"][0]
    }, broadcast=True)

@socketio.on('submit_answer')
def handle_submit_answer(data):
    index = game_state["current_index"]
    correct = game_state["questions"][index]["correct"]
    is_correct = data["answer"] == correct
    score = data["score"] if is_correct else 0

    print(f"Answer: {data['answer']} | Correct: {correct} | Score: {score}")

    emit("answer_result", {
        "correct": is_correct,
        "correct_index": correct,
        "score": score
    }, broadcast=True)

    if index + 1 < 10:
        game_state["current_index"] += 1
        next_question = game_state["questions"][game_state["current_index"]]
        emit("show_question", {
            "index": game_state["current_index"],
            "question": next_question
        }, broadcast=True)
    else:
        emit("game_over", {}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
