import os
import requests
import streamlit as st

# This will be set as an env var in Render or docker-compose
RASA_API_URL = os.getenv(
    "RASA_API_URL",
    "http://localhost:5005/webhooks/rest/webhook"
)

st.set_page_config(page_title="AI Health Chatbot", page_icon="💬")

st.title("💬 AI Health Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# show previous messages
for sender, msg in st.session_state.messages:
    if sender == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Bot:** {msg}")

user_input = st.text_input("Type your message:", "")

if st.button("Send") and user_input.strip():
    st.session_state.messages.append(("user", user_input))

    try:
        resp = requests.post(
            RASA_API_URL,
            json={"sender": "web-user", "message": user_input},
            timeout=10
        )
        bot_text = ""
        if resp.ok:
            data = resp.json()
            if data:
                bot_text = data[0].get("text", "")
        if not bot_text:
            bot_text = "(No response received.)"
    except Exception as e:
        bot_text = f"(Error talking to server: {e})"

    st.session_state.messages.append(("bot", bot_text))
    st.experimental_rerun()
