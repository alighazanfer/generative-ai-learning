from models import model
from schemas import GlobalState
from models import embedding_model
from langgraph.types import interrupt, Command
from prompts import budget_planner_prompt, itinerary_prompt
from chains import LLM_ROUTER_CHAIN, DESIGNATION_INFO_CHAIN
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def format_history(history: str) -> str:
    messages = history.strip().split("\n")
    return "\n".join(messages[-3:])


def llm_router_node(state: GlobalState):
    state.casual_answer = None 

    router_decision = LLM_ROUTER_CHAIN.invoke({
        "query": state.query,
        "history": format_history(state.history)
    })

    if router_decision.status == "CASUAL":
        state.casual_answer = router_decision.answer

    return state


def destination_info_node(state: GlobalState):
    loader = PyPDFLoader("worldwide-travel-guide.pdf")
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    vector_store = InMemoryVectorStore(embedding_model)
    _ = vector_store.add_documents(all_splits)

    retrieved_docs = vector_store.similarity_search(state.query, k=3)
    docs_context_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

    designation_info = DESIGNATION_INFO_CHAIN.invoke({
        "query": state.query,
        "context": docs_context_content,
        "history": format_history(state.history)
    })

    state.designation_info = designation_info
    if not designation_info.found:
        state.casual_answer = "Sorry, I don't have information about that city. Could you try another?"

    return state


def flight_info_node(state: GlobalState):
    state.flight_info = "flight price is $2000."
    return state


def weather_info_node(state: GlobalState):
    state.weather_info = "weather is rainy."
    return state


def budget_planner_node(state: GlobalState):
    messages = budget_planner_prompt.invoke({
        "designation_info": state.designation_info,
        "flight_info": state.flight_info,
        "query": state.query,
        "history": format_history(state.history)
    })

    response = model.invoke(messages)
    state.budget_info = response.content

    response = interrupt({ "budget_info": state.budget_info })
    user_feedback = response.get("user_feedback", "").strip().lower()
    if user_feedback == "proceed":
        return Command(goto="itinerary_node")
    else:
        state.casual_answer = "Okay, I won’t proceed."
        return state


def itinerary_node(state: GlobalState):
    messages = itinerary_prompt.invoke({
        "designation_info": state.designation_info,
        "weather_info": state.weather_info,
        "flight_info": state.flight_info,
        "budget_info": state.budget_info,
        "query": state.query,
        "history": format_history(state.history)
    })

    response = model.invoke(messages)
    state.itinerary = response.content
    return state
