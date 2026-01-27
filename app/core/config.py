from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agentic RAG Question Service"
    API_V1_STR: str = "/api/v1"
    
    OPENAI_API_KEY: str
    
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "questions_rag"
    
    MODEL_NAME: str = "gpt-4.1"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    TEMPERATURE: float = 0.5
    
    MAX_ITERATIONS: int = 3
    TOP_K_CONTEXT: int = 5

    RAG_CHUNK_SIZE: int = 768
    RAG_CHUNK_OVERLAP: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
