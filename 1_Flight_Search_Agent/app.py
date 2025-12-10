from main import retrieval_agent
import streamlit as st

st.set_page_config(
    page_title="AeroAssistant",
    layout="centered"
)

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
        .main {
            font-family: 'Inter', sans-serif;
            background-color: #F8F9FC;
        }
        
        /* Remove the fixed positioning that was causing the issue */
        .stChatInput {
            position: relative !important;
            bottom: auto !important;
            width: 100% !important;
        }
        
        .chat-messages {
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)


def run_flight_assistant():
    st.title("**FLIGHT ASSISTANT**")
    st.divider()
    
    # -------------------- SESSION STATE --------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # -------------------- CHAT INTERFACE --------------------
    st.subheader("Chat with your Flight Assistant")
    
    # Display chat history with Streamlit's native chat bubbles
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input bar - this should now be centered properly
    user_input = st.chat_input("Type your flight question here...")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                try:
                    response = ask_flight(user_input)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error retrieving flight information: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.rerun()


if __name__ == "__main__":
    run_flight_assistant()