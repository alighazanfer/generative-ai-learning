import os
import asyncio
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langgraph.graph import START, END, StateGraph
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise ValueError("OPENAI_API_KEY not found in environment variables.")

class State(TypedDict):
    route: str
    context: List[Document]
    question: str
    answer: str
    history: str


llm_router_prompt = PromptTemplate(
    input_variables=["question", "history"],
    template="""
        You are having a conversation. Here are the last 3 messages of history: {history}

        Decide if you can answer the user's latest message using only the conversation history or your general knowledge.
        - If the answer requires the external document, respond with exactly one word: "RAG".
        - If you can answer from history or your own knowledge, provide the answer directly.

        Question: {question}

        Response:
    """
)

rag_prompt = PromptTemplate(
    input_variables=["question", "context", "history"],
    template="""
        You are having a conversation. Here are the last 3 messages of history: {history}

        Use the following pieces of context to answer the question at the end:
        - If you don't know the answer, just say that you don't know, don't try to make up an answer.
        - Use three sentences maximum and keep the answer as concise as possible.

        {context}

        Question: {question}

        Helpful Answer:
    """
)

def format_history(history: str) -> str:
    messages = history.strip().split("\n")
    return "\n".join(messages[-3:])

def build_pdf_rag_graph(pdf_path: str):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    # model = init_chat_model("gpt-4o-mini", model_provider="openai")
    # embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    vector_store = InMemoryVectorStore(embeddings)
    _ = vector_store.add_documents(all_splits)

    def llm_router_node(state: State):
        message = llm_router_prompt.invoke({
            "question": state["question"],
            "history": format_history(state["history"])
        })
        router_response = model.invoke(message)

        if router_response.content.strip().lower() == "rag":
            state["route"] = "rag"
        else:
            state["route"] = "direct"

        if state["route"] == "direct":
            state["answer"] = router_response.content

        return state

    def rag_node(state: State):
        retrieved_docs = vector_store.similarity_search(state["question"])
        docs_context_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

        messages = rag_prompt.invoke({
            "question": state["question"],
            "context": docs_context_content,
            "history": format_history(state["history"])
        })
        
        response = model.invoke(messages)
        state["answer"] = response.content
        return state
        
    graph_builder = StateGraph(State)
    graph_builder.add_node("llm_router", llm_router_node)
    graph_builder.add_node("rag", rag_node)

    graph_builder.add_edge(START, "llm_router")
    graph_builder.add_conditional_edges(
        "llm_router",
        lambda s: s["route"],
        {
            "rag": "rag",
            "direct": END
        }
    )
    graph_builder.add_edge("rag", END)

    return graph_builder.compile()
