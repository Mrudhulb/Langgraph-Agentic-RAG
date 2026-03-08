import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Directory Configuration ---
MARKDOWN_DIR = "markdown_docs"
PARENT_STORE_PATH = "parent_store"
QDRANT_DB_PATH = "qdrant_db"

# --- Qdrant Configuration ---
CHILD_COLLECTION = "document_child_chunks"
SPARSE_VECTOR_NAME = "sparse"

# --- Model Configuration ---
DENSE_MODEL = "BAAI/bge-large-en-v1.5" # <your_dense_model_name>
SPARSE_MODEL = "Qdrant/bm25"
LLM_MODEL = "qwen3:4b-instruct-2507-q4_K_M" # <your_LLM_model_name>
LLM_TEMPERATURE = 0

# --- Text Splitter Configuration ---
CHILD_CHUNK_SIZE = 500
CHILD_CHUNK_OVERLAP = 100
MIN_PARENT_SIZE = 2000
MAX_PARENT_SIZE = 10000
HEADERS_TO_SPLIT_ON = [
    ("#", "H1"),
    ("##", "H2"),
    ("###", "H3")
]


# --- Multi-Provider LLM Configuration ---
LLM_CONFIGS = {
    "ollama": {
        "model": "llama3.2:3b", # <your_Ollama_model_name>
        "url":"http://localhost:11434", # <your_Ollama_url>
        "temperature": 0
    },
    "openai": {
        "model": "gpt-4o", # <your_OpenAI_model_name>
        "temperature": 0,
        "api_key": os.getenv("OPENAI_API_KEY", "<your_api_key>")
    },
    "openrouter": {
        "model": "nvidia/nemotron-3-nano-30b-a3b:free", # <your_OpenRouter_model_name>
        "temperature": 0,
        "api_key": os.getenv("OPENROUTER_API_KEY", "<your_api_key>")
    },
    "anthropic": {
        "model": "claude-sonnet-4-20250514", # <your_Anhropic_model_name>
        "temperature": 0,
        "api_key": os.getenv("ANTHROPIC_API_KEY", "<your_api_key>")
    },
    "google": {
        "model": "gemini-2.5-flash", # <your_Google_model_name>
        "temperature": 0,
        "api_key": os.getenv("GOOGLE_API_KEY", "<your_api_key>")
    }
}

# Switch providers by changing this single line
ACTIVE_LLM_CONFIG = "openrouter" # <your_active_provider_name>

# --- LangSmith Tracing ---
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "<your_api_key>") # <your_api_key>
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "<your_project_name>") # <your_project_name>

# --- OCR Configuration ---
OCR_ENABLED = True # Set to True to enable auto-OCR for image-based PDFs
OCR_MODEL = '<your_VLM_model_name>' # <your_VLM_model_name>

# --- Tavily Search Configuration ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "<your_tavily_api_key>") # <your_tavily_api_key>