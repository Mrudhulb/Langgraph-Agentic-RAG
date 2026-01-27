import uuid
from langchain_ollama import ChatOllama
import config
from db.vector_db_manager import VectorDbManager
from db.parent_store_manager import ParentStoreManager
from document_chunker import DocumentChuncker
from rag_agent.tools import ToolFactory
from rag_agent.graph import create_agent_graph

class RAGSystem:
    
    def __init__(self, collection_name=config.CHILD_COLLECTION):
        self.collection_name = collection_name
        self.vector_db = VectorDbManager()
        self.parent_store = ParentStoreManager()
        self.chunker = DocumentChuncker()
        self.agent_graph = None
        self.thread_id = str(uuid.uuid4())
        
    def initialize(self):
        print(f"DEBUG: Initializing RAGSystem with config {config.ACTIVE_LLM_CONFIG}")
        self.vector_db.create_collection(self.collection_name)
        collection = self.vector_db.get_collection(self.collection_name)
    
        # Load active configuration
        active_config = config.LLM_CONFIGS[config.ACTIVE_LLM_CONFIG]
        model = active_config["model"]
        temperature = active_config["temperature"]
    
    
        if config.ACTIVE_LLM_CONFIG == "ollama":
            from langchain_ollama import ChatOllama
            llm = ChatOllama(model=model, temperature=temperature, base_url=active_config["url"])
        
        elif config.ACTIVE_LLM_CONFIG == "openai":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model=model, temperature=temperature, openai_api_key=active_config["api_key"])
        
        elif config.ACTIVE_LLM_CONFIG == "anthropic":
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(model=model, temperature=temperature)
        
        elif config.ACTIVE_LLM_CONFIG == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
        
        elif config.ACTIVE_LLM_CONFIG == "openrouter":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model=model, temperature=temperature, 
            openai_api_key=active_config["api_key"],
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
        "HTTP-Referer": "https://localhost:3000", # Required for OpenRouter rankings
        "X-Title": "Agentic-RAG",        # Shows up in your OpenRouter dashboard
    }
)
        
        else:
            raise ValueError(f"Unsupported LLM provider: {config.ACTIVE_LLM_CONFIG}")
    
        # Continue with tool and graph initialization
        tools = ToolFactory(collection).create_tools()
        self.agent_graph = create_agent_graph(llm, tools)
        
    def get_config(self):
        return {"configurable": {"thread_id": self.thread_id}}
    
    def reset_thread(self):
        try:
            self.agent_graph.checkpointer.delete_thread(self.thread_id)
        except Exception as e:
            print(f"Warning: Could not delete thread {self.thread_id}: {e}")
        self.thread_id = str(uuid.uuid4())