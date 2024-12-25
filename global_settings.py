LOG_FILE = "session_data/user_actions.log"
SESSION_FILE = "session_data/user_session_state.yaml"
CACHE_FILE = "cache/pipeline_cache.json"
CONVERSATION_FILE = "cache/chat_history.json"
QUIZ_FILE = "cache/quiz.csv"
SLIDES_FILE = "cache/slides.json"
STORAGE_PATH = "ingestion_storage/"
INDEX_STORAGE = "index_storage"
QUIZ_SIZE = 5
ITEMS_ON_SLIDE = 4

# Model settings
DEFAULT_MODEL_PROVIDER = "openai"  # can be "openai" or "ollama"
DEFAULT_OLLAMA_MODEL = "qwen2.5:0.5b"

import os

# Create directories if they don't exist
os.makedirs("session_data", exist_ok=True)
os.makedirs("cache", exist_ok=True)
os.makedirs(STORAGE_PATH, exist_ok=True)
os.makedirs(INDEX_STORAGE, exist_ok=True)
