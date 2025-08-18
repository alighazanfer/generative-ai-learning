import streamlit as st
from main import build_graph
from langgraph.types import Command


# Initialize session state
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'graph' not in st.session_state:
    st.session_state['graph'] = build_graph()
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = "1"
if 'waiting_for_approval' not in st.session_state:
    st.session_state['waiting_for_approval'] = False


# Interface setup
st.title("Travel Planner")
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
user_input = st.chat_input('Type here')


# Handle user input and invoke the graph
if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        config = {"configurable": {"thread_id": st.session_state['thread_id']}}
        
        if st.session_state['waiting_for_approval']:
            state = st.session_state['graph'].invoke(Command(resume=user_input), config)
            st.session_state['waiting_for_approval'] = False
        else:
            state = st.session_state['graph'].invoke({"query": user_input}, config)

        if "__interrupt__" in state:
            st.session_state['waiting_for_approval'] = True
            interrupt_data = state["__interrupt__"][0].value
            message = interrupt_data.get("budget_info", "")
            st.session_state['message_history'].append({'role': 'assistant', 'content': message})
            with st.chat_message('assistant'):
                st.markdown(message)
        else:
            assistant_reply = state.get("casual_answer") or state.get("itinerary")
            st.session_state['message_history'].append({'role': 'assistant', 'content': assistant_reply})
            with st.chat_message('assistant'):
                st.markdown(assistant_reply)
