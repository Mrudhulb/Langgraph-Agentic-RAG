# --- Directory Configuration ---
MARKDOWN_DIR = "markdown_docs"
PARENT_STORE_PATH = "parent_store"
QDRANT_DB_PATH = "qdrant_db"

# --- Qdrant Configuration ---
CHILD_COLLECTION = "document_child_chunks"
SPARSE_VECTOR_NAME = "sparse"

# --- Model Configuration ---
DENSE_MODEL = "BAAI/bge-large-en-v1.5"
SPARSE_MODEL = "Qdrant/bm25"
LLM_MODEL = "qwen3:4b-instruct-2507-q4_K_M"
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
        "model": "llama3.2:3b",
        "url":"http://localhost:11434",
        "temperature": 0
    },
    "openai": {
        "model": "gpt-4o",
        "temperature": 0
    },
    "openrouter": {
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "temperature": 0,
        "api_key": "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"
    },
    "anthropic": {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0
    },
    "google": {
        "model": "gemini-2.5-flash",
        "temperature": 0
    }
}

# Switch providers by changing this single line
ACTIVE_LLM_CONFIG = "openrouter"