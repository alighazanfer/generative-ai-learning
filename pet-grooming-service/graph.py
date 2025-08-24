from models import GlobalState
from nodes import initiate_lead, qualify_lead
from langgraph.graph import StateGraph, START, END


graph = StateGraph(GlobalState)

graph.add_node("initiate_lead", initiate_lead)
graph.add_node("qualify_lead", qualify_lead)

graph.add_edge(START, "initiate_lead")
graph.add_edge("initiate_lead", "qualify_lead")
graph.add_edge("qualify_lead", END)

query = input("What you want to ask?")
graph.invoke({"query": query})
