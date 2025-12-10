import streamlit as st
from datetime import datetime
import sys
import os

# ------------------ IMPORT MASTER AGENT ------------------ #
# Make sure the path to Master/main.py is correct
sys.path.append(os.path.join(os.getcwd(), "Multi_Agents_Flight_Intelligence", "Master"))
from main import master_agent  # Import your master agent function

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(
    page_title="SkyVista Master Agent",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------ STYLING ------------------ #
st.markdown(
    """
    <style>
    .stTextInput>div>div>input {
        height: 50px;
        font-size: 16px;
    }
    .stButton>button {
        height: 50px;
        font-size: 16px;
    }
    .message-container {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .user-message {
        background-color: #d1e7dd;
    }
    .agent-message {
        background-color: #e2e3e5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ HEADER ------------------ #
st.title("SkyVista Master Agent")
st.markdown("Your AI assistant for flight search, booking, and help.")

# ------------------ SESSION STATE ------------------ #
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ DISPLAY CHAT ------------------ #
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    time = msg["time"].strftime("%H:%M")
    if role == "user":
        st.markdown(f'<div class="message-container user-message"><b>You [{time}]:</b> {content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="message-container agent-message"><b>SkyVista [{time}]:</b> {content}</div>', unsafe_allow_html=True)

# ------------------ USER INPUT ------------------ #
def submit_message():
    user_msg = st.session_state.user_input.strip()
    if user_msg:
        # Save user message
        st.session_state.messages.append({"role": "user", "content": user_msg, "time": datetime.now()})
        st.session_state.user_input = ""

        # Get agent response
        try:
            agent_response = master_agent(user_msg)  # Call the Master Agent function
        except Exception as e:
            agent_response = f"Error: {str(e)}"

        # Save agent message
        st.session_state.messages.append({"role": "agent", "content": agent_response, "time": datetime.now()})

# Input box
st.text_input("Type your message here...", key="user_input", on_change=submit_message)

# ------------------ CLEAR CHAT BUTTON ------------------ #
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun()
