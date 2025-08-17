import json
from models import model
from states import GlobalState
from models import model, embedding_model
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from prompts import llm_router_prompt, city_info_prompt, budget_planner_prompt


def llm_router_node(state: GlobalState):
    message = llm_router_prompt.invoke({ "query": state["query"] })
    response = model.invoke(message)
    router_decision = json.loads(response.content)
    
    if router_decision["status"] == "CASUAL":
        state["casual_answer"] = router_decision["answer"]
    elif router_decision["status"] == "PLANNING":
        state["casual_answer"] = None
    else:
        state["casual_answer"] = "Something went wrong, please try again!"

    return state


def city_info_node(state: GlobalState):
    loader = PyPDFLoader("worldwide-travel-guide.pdf")
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    vector_store = InMemoryVectorStore(embedding_model)
    _ = vector_store.add_documents(all_splits)

    retrieved_docs = vector_store.similarity_search(state["query"], k=3)
    docs_context_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

    messages = city_info_prompt.invoke({
        "query": state["query"],
        "context": docs_context_content,
    })  
    response = model.invoke(messages)
    designation_info = json.loads(response.content)
    state["designation_info"] = designation_info

    return state


def flight_info_node(state: GlobalState):
    if state["designation_info"]["found"] is False:
        state["casual_answer"] = "Sorry, I don't have information about that city. Could you try another?"
        return state

    # TODO: use api to fetch flights info
    # designation_name = state["designation_info"]["designation_name"]
    # airport_iata = get_airport_iata(designation_name)

    state["flight_info"] = "3 flight are avilable for going to that city."
    return state


def weather_info_node(state: GlobalState):
    # TODO: use api to fetch weather info
    # designation_name = state["designation_info"]["designation_name"]
    # weather_report = get_weather(designation_name)
    state["weather_info"] = "weather is sunny."
    return state


def budget_planner_node(state: GlobalState):
    messages = budget_planner_prompt.invoke({
        "designation_info": state["designation_info"],
        "flight_info": state["flight_info"],
        "weather_info": state["weather_info"],
        "query": state["query"]
    })
    response = model.invoke(messages)
    budget_info = json.loads(response.content)
    state["budget_info"] = budget_info
    return state
