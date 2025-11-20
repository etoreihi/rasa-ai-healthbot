from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder=".", static_url_path="")

RASA_URL = "http://web-production-cde1.up.railway.app"

@app.route("/")
def index():
    return send_from_directory("ui", "index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_message = request.json.get("message", "")

    res = requests.post(RASA_URL, json={"sender": "user", "message": user_message})
    bot_response = res.json()

    # Rasa responds as a list — return text only
    texts = [m.get("text", "") for m in bot_response]

    return jsonify({"responses": texts})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
