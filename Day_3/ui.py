import os
import tempfile
import streamlit as st
from main import build_pdf_rag_graph


# Upload pdf interface
with st.sidebar:
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file:
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

        st.session_state["pdf_path"] = temp_path


# Initialize and load previous messages
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


# message of user and assistant interface
user_input = st.chat_input('Type here')

if user_input and "pdf_path" in st.session_state:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.spinner("Thinking..."):
        if len(st.session_state['message_history']) > 1:
            history_messages = st.session_state['message_history'][-3:]
            history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history_messages])
        else:
            history_text = ""
            
        graph = build_pdf_rag_graph(st.session_state["pdf_path"])
        state = graph.invoke({ "question": user_input, "history": history_text })

    st.session_state['message_history'].append({'role': 'assistant', 'content': state["answer"]})
    with st.chat_message('assistant'):
        st.text(state["answer"])  

elif user_input:
    st.warning("Please upload a PDF first!")
