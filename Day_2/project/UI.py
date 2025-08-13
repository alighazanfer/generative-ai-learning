import streamlit as st
from main import get_agent_response

st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"**You:** {user_input}")

    with st.spinner("Thinking..."):
        bot_response = get_agent_response(user_input)
        
    st.session_state.messages.append({"role": "bot", "content": bot_response})
    st.rerun()
    