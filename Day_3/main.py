import os
import asyncio
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
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

class State(TypedDict):
    context: List[Document]
    question: str
    answer: str


rag_prompt = PromptTemplate(
    input_variables=["question", "context"],
    template="""
        If the question is a greeting (e.g., "hi", "hello", "hey", "good morning", etc.), respond only with a friendly greeting and ask how you may help — ignore the context.

        Otherwise, use the following pieces of context to answer the question at the end:
        - If you don't know the answer, just say that you don't know, don't try to make up an answer.
        - Use three sentences maximum and keep the answer as concise as possible.
        - Always say "thanks for asking!" at the end of the answer.

        {context}

        Question: {question}

        Helpful Answer:
    """
)


def build_pdf_rag_graph(pdf_path: str):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    vector_store = InMemoryVectorStore(embeddings)
    _ = vector_store.add_documents(all_splits)

    def retrieve(state: State):
        retrieved_docs = vector_store.similarity_search(state["question"])
        return {"context": retrieved_docs}

    def generate(state: State):
        docs_context_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = rag_prompt.invoke({ "question": state["question"], "context": docs_context_content })
        response = model.invoke(messages)
        return {"answer": response.content}
        
    graph_builder = StateGraph(State)
    graph_builder.add_node("retrieve", retrieve)
    graph_builder.add_node("generate", generate)

    graph_builder.add_edge(START, "retrieve")
    graph_builder.add_edge("retrieve", "generate")
    graph_builder.add_edge("generate", END)

    return graph_builder.compile()


# For CLI
# graph = build_pdf_rag_graph("invoice_1.pdf")
# user_input = input("How may I help you? \n")
# state = graph.invoke({ "question": user_input })
# print(state["answer"])
