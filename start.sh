#!/bin/bash

# Start Rasa Server (API enabled)
rasa run --enable-api --cors "*" --port 5005 &

# Start Action Server
rasa run actions --port 5055 &

# Start Flask UI
python ui/server.py
