import os
from dotenv import load_dotenv
from typing import Optional

# 加载环境变量
load_dotenv()

class Config:
    """配置管理类"""
    
    # LLM 配置
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Ollama 配置
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gpt-3.5-turbo:latest")
    
    # 向量数据库配置
    VECTOR_DB: str = os.getenv("VECTOR_DB", "chroma")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # Pinecone 配置
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "babyagi-tasks")
    
    # 任务配置
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "5"))
    OBJECTIVE: str = os.getenv("OBJECTIVE", "Develop a task list")
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "babyagi.log")
    
    # API 配置
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "5000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "true").lower() == "true"
    
    # Web 界面配置
    WEB_HOST: str = os.getenv("WEB_HOST", "0.0.0.0")
    WEB_PORT: int = int(os.getenv("WEB_PORT", "7860"))
    
    # Redis 配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否有效"""
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("使用 OpenAI 时必须设置 OPENAI_API_KEY")
        
        if cls.VECTOR_DB == "pinecone" and (not cls.PINECONE_API_KEY or not cls.PINECONE_ENVIRONMENT):
            raise ValueError("使用 Pinecone 时必须设置 PINECONE_API_KEY 和 PINECONE_ENVIRONMENT")
        
        return True
    
    @classmethod
    def get_summary(cls) -> dict:
        """获取配置摘要（不包含敏感信息）"""
        return {
            "llm_provider": cls.LLM_PROVIDER,
            "openai_model": cls.OPENAI_MODEL if cls.LLM_PROVIDER == "openai" else None,
            "ollama_model": cls.OLLAMA_MODEL if cls.LLM_PROVIDER == "ollama" else None,
            "vector_db": cls.VECTOR_DB,
            "max_iterations": cls.MAX_ITERATIONS,
            "log_level": cls.LOG_LEVEL
        }

# 全局配置实例
config = Config()