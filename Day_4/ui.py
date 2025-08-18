import streamlit as st
from main import build_graph

# Initialize session states
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'graph' not in st.session_state:
    st.session_state['graph'] = build_graph()
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = "default-thread" 

# Display previous messages
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# User input
user_input = st.chat_input('Type here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    with st.spinner("Thinking..."):
        config = {"configurable": {"thread_id": st.session_state['thread_id']}}
        state = st.session_state['graph'].invoke({ "query": user_input }, config)
        
    assistant_reply = state.get("casual_answer") or state.get("itinerary")
    st.session_state['message_history'].append({'role': 'assistant', 'content': assistant_reply})
    with st.chat_message('assistant'):
        st.markdown(assistant_reply)
