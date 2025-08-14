import streamlit as st
import os
from langchain import hub
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langchain.chat_models import init_chat_model
from langgraph.graph import START, END, StateGraph
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

class State(TypedDict):
    context: List[Document]
    question: str
    answer: str

# Page configuration
st.set_page_config(
    page_title="PDF RAG Chatbot",
    page_icon="📚",
    layout="wide"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check for API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")
    st.stop()

@st.cache_resource
def initialize_model_and_embeddings():
    """Initialize the model and embeddings once and cache them."""
    import asyncio
    import nest_asyncio
    
    # Apply nest_asyncio to handle nested event loops
    nest_asyncio.apply()
    
    # Create new event loop for this thread
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return model, embeddings

@st.cache_resource
def build_pdf_rag_graph(pdf_path: str):
    """Build and cache the RAG graph for the PDF."""
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        rag_prompt = hub.pull("rlm/rag-prompt")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)
        
        model, embeddings = initialize_model_and_embeddings()
        vector_store = Chroma.from_documents(all_splits, embeddings)

        def retrieve(state: State):
            retrieved_docs = vector_store.similarity_search(state["question"])
            return {"context": retrieved_docs}

        def generate(state: State):
            docs_context_content = "\n\n".join(doc.page_content for doc in state["context"])
            messages = rag_prompt.invoke({"question": state["question"], "context": docs_context_content})
            response = model.invoke(messages)
            return {"answer": response.content}

        graph_builder = StateGraph(State)
        graph_builder.add_node("retrieve", retrieve)
        graph_builder.add_node("generate", generate)

        graph_builder.add_edge(START, "retrieve")
        graph_builder.add_edge("retrieve", "generate")
        graph_builder.add_edge("generate", END)

        return graph_builder.compile()
    except Exception as e:
        st.error(f"Error building RAG graph: {str(e)}")
        return None

# Main app
def main():
    st.title("📚 PDF RAG Chatbot")
    st.markdown("Ask questions about your PDF document and get AI-powered answers!")
    
    # Check if PDF exists
    pdf_path = "invoice_1.pdf"
    if not os.path.exists(pdf_path):
        st.error(f"PDF file '{pdf_path}' not found. Please ensure the file exists in the same directory.")
        st.stop()
    
    # Initialize the RAG graph
    with st.spinner("Loading PDF and building RAG system..."):
        graph = build_pdf_rag_graph(pdf_path)
    
    if graph is None:
        st.error("Failed to initialize the RAG system. Please check your configuration.")
        st.stop()
    
    st.success("✅ PDF loaded and RAG system ready!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your PDF..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant message
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 Thinking...")
            
            try:
                # Get response from RAG system with proper async handling
                import asyncio
                
                # Create new event loop for this thread if needed
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Run the graph invocation
                state = graph.invoke({"question": prompt})
                answer = state["answer"]
                
                # Update placeholder with actual response
                message_placeholder.markdown(answer)
                
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This chatbot uses:
        - **RAG (Retrieval-Augmented Generation)** to answer questions
        - **Google Gemini 2.5 Flash** for AI responses
        - **ChromaDB** for vector storage
        - **LangGraph** for workflow orchestration
        """)
        
        st.header("📊 Chat Stats")
        st.metric("Total Messages", len(st.session_state.messages))
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()
