from schemas import GlobalState
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from nodes import llm_router_node, destination_info_node, flight_info_node, weather_info_node, budget_planner_node, itinerary_node

def build_graph():
    graph_builder = StateGraph(GlobalState)
    
    graph_builder.add_node("llm_router", llm_router_node)
    graph_builder.add_node("destination_info_node", destination_info_node)
    graph_builder.add_node("flight_info_node", flight_info_node)
    graph_builder.add_node("weather_info_node", weather_info_node)
    graph_builder.add_node("budget_planner_node", budget_planner_node)
    graph_builder.add_node("itinerary_node", itinerary_node)
    
    graph_builder.add_edge(START, "llm_router")
    graph_builder.add_conditional_edges(
        "llm_router",
        lambda state: "STOP" if state.casual_answer is not None else "NEXT_NODE",
        {
            "STOP": END,
            "NEXT_NODE": "destination_info_node"
        }
    )
    graph_builder.add_conditional_edges(
        "destination_info_node",
        lambda state: "NEXT_NODE" if state.designation_info.found else "STOP",
        {
            "STOP": END,
            "NEXT_NODE": "flight_info_node"
        }
    )
    graph_builder.add_edge("flight_info_node", "weather_info_node")
    graph_builder.add_edge("weather_info_node", "budget_planner_node")
    graph_builder.add_edge("budget_planner_node", END)
    graph_builder.add_edge("itinerary_node", END)
    
    checkpointer = InMemorySaver()
    return graph_builder.compile(checkpointer=checkpointer)
