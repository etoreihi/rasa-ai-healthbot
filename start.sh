#!/bin/bash

# Start Rasa API
rasa run --enable-api --cors "*" &

# Start Action Server
rasa run actions &

# Start UI
streamlit run ui/app.py --server.port $PORT --server.address 0.0.0.0
