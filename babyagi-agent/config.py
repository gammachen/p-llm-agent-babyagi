import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM 配置
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, ollama, anthropic
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Ollama 配置
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # 向量数据库配置
    VECTOR_DB = os.getenv("VECTOR_DB", "chroma")  # chroma, pinecone, weaviate
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # 任务配置
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", 5))
    OBJECTIVE = os.getenv("OBJECTIVE", "Develop a task list")
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "babyagi.log")
    
    # LLM 调用配置
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 120))  # LLM调用超时时间（秒）
    LLM_RETRY_ATTEMPTS = int(os.getenv("LLM_RETRY_ATTEMPTS", 3))  # LLM调用重试次数