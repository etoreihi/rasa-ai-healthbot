from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    response = requests.post(
        RASA_URL,
        json={"sender": "user", "message": user_message}
    )

    if response.status_code != 200:
        return jsonify({"error": "Rasa error"}), 500

    rasa_reply = response.json()
    text = rasa_reply[0].get("text", "") if rasa_reply else ""

    return jsonify({"reply": text})

@app.route("/", methods=["GET"])
def home():
    return "Flask API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
