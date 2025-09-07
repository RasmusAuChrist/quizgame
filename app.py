from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random, json, os
from threading import Timer

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load all available questions
with open("questions.json", "r") as f:
    all_questions = json.load(f)

# Initialize game state
game_state = {
    "player": None,
    "questions": [],
    "current_index": 0,
    "score": 0
}

def reset_game():
    game_state["player"] = None
    game_state["questions"] = []
    game_state["current_index"] = 0
    game_state["score"] = 0
    print("Game state reset.")
    socketio.emit("reset_game")

def save_score(name, score):
    filename = "scores.json"
    scores = []

    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                scores = json.load(f)
            except json.JSONDecodeError:
                pass

    scores.append({ "name": name, "score": score })
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]

    with open(filename, "w") as f:
        json.dump(scores, f)

    return scores

@app.route('/')
def screen():
    return render_template('screen.html')

@app.route('/phone')
def phone():
    return render_template('phone.html')

@socketio.on('player_joined')
def handle_player_joined(data):
    name = data['name']
    print(f"Player joined: {name}")
    game_state["player"] = name
    game_state["questions"] = random.sample(all_questions, 10)
    game_state["current_index"] = 0
    game_state["score"] = 0

    emit("player_joined", { "name": name }, broadcast=True)
    emit("show_question", {
        "index": 0,
        "question": game_state["questions"][0]
    }, broadcast=True)

@socketio.on('submit_answer')
def handle_submit_answer(data):
    index = game_state["current_index"]
    correct_index = game_state["questions"][index]["correct"]
    is_correct = data["answer"] == correct_index
    awarded_score = data["score"] if is_correct else 0
    game_state["score"] += awarded_score

    emit("answer_result", {
        "correct": is_correct,
        "correct_index": correct_index,
        "score": awarded_score
    }, broadcast=True)

    if index + 1 < 10:
        game_state["current_index"] += 1
        next_q = game_state["questions"][game_state["current_index"]]
        emit("show_question", {
            "index": game_state["current_index"],
            "question": next_q
        }, broadcast=True)
    else:
        # Game over: save score and send leaderboard
        leaderboard = save_score(game_state["player"], game_state["score"])
        emit("game_over", {
            "score": game_state["score"],
            "leaderboard": leaderboard,
            "player": game_state["player"]
        }, broadcast=True)

        # Reset after 15 seconds
        Timer(15.0, reset_game).start()
