from langgraph.graph import END
from models import model
from schemas import GlobalState
from models import embedding_model
from langgraph.types import interrupt, Command
from prompts import budget_planner_prompt, itinerary_prompt
from chains import LLM_ROUTER_CHAIN, DESIGNATION_INFO_CHAIN
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def llm_router_node(state: GlobalState):
    router_decision = LLM_ROUTER_CHAIN.invoke({ "query": state.query })
    print("router_decision", router_decision)

    if router_decision.status == "CASUAL":
        state.casual_answer = router_decision.answer

    return state


def city_info_node(state: GlobalState):
    print("city_info_node")
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
        "query": state.query
    })

    response = model.invoke(messages)
    state.budget_info = response.content

    is_approved = interrupt(
        {
            "question": "Do you want to proceed with this budget plan?",
            "budget_output": state.budget_info,
            "flight_info": state.flight_info,
            "designation_info": state.designation_info,
            "weather_info": state.weather_info,
            "query": state.query
        }
    )

    if is_approved:
        return Command(goto="itinerary_node")
    else:
        return Command(goto="budget_planner_node")


def itinerary_node(state: GlobalState):
    messages = itinerary_prompt.invoke({
        "designation_info": state.designation_info,
        "weather_info": state.weather_info,
        "flight_info": state.flight_info,
        "budget_info": state.budget_info,
        "query": state.query
    })

    response = model.invoke(messages)
    state.itinerary = response.content
    return state
