#!/bin/bash
# Start Rasa action server in background
rasa run actions &
sleep 3

# Start Rasa shell
rasa shell
