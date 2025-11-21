from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder="static")
CORS(app)

RASA_URL = os.environ.get("RASA_URL", "http://0.0.0.0:5005/webhooks/rest/webhook")




@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    response = requests.post(RASA_URL, json={"sender": "user", "message": user_msg})
    return jsonify(response.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
