#!/bin/bash
set -e

echo "Starting Rasa server..."
rasa run --enable-api --cors "*" --port 5005 &

echo "Starting Rasa action server..."
rasa run actions --port 5055 &

echo "Starting Flask UI..."
python ui/server.py
