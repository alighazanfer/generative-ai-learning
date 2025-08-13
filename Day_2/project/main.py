import os
from langchain import hub
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import tool, create_react_agent, AgentExecutor

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(
    model="gpt-4",
    api_key=OPENAI_API_KEY,
    temperature=0
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

@tool
def get_current_time(query: str) -> str:
    """Returns the current date and time in 12 hour formate."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools = [get_current_time]

prompt = hub.pull("hwchase17/react")
agent = create_react_agent(model, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

def get_agent_response(user_input: str) -> str:
    """Invoke the ReAct agent with user input."""
    response = agent_executor.invoke({"input": user_input})
    return response["output"]
