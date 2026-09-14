import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Document ingestion / embeddings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

MAX_DOCUMENT_WORDS = 10000
CHUNK_WORD_SIZE = 400
CHUNK_WORD_OVERLAP = 50

# Question answering
GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-3.6-flash")
QA_TOP_K_CHUNKS = 5
