"""
应用配置管理
"""
import os
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本配置
    app_name: str = "Education Agent System"
    app_version: str = "0.1.0"
    debug: bool = Field(default=True, env="DEBUG")
    
    # API配置
    api_prefix: str = "/api/v1"
    
    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./education_agent.db",
        env="DATABASE_URL"
    )
    
    # LLM模型配置
    llm_provider: Literal["openai", "azure", "deepseek", "qwen", "claude"] = Field(
        default="openai",
        env="LLM_PROVIDER"
    )
    
    # OpenAI配置
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_api_base: str = Field(
        default="https://api.openai.com/v1",
        env="OPENAI_API_BASE"
    )
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    
    # Azure OpenAI配置
    azure_api_key: str = Field(default="", env="AZURE_API_KEY")
    azure_api_base: str = Field(default="", env="AZURE_API_BASE")
    azure_api_version: str = Field(default="2023-05-15", env="AZURE_API_VERSION")
    azure_deployment_name: str = Field(default="", env="AZURE_DEPLOYMENT_NAME")
    
    # DeepSeek配置
    deepseek_api_key: str = Field(default="", env="DEEPSEEK_API_KEY")
    deepseek_api_base: str = Field(
        default="https://api.deepseek.com/v1",
        env="DEEPSEEK_API_BASE"
    )
    deepseek_model: str = Field(default="deepseek-chat", env="DEEPSEEK_MODEL")
    
    # Qwen配置
    qwen_api_key: str = Field(default="", env="QWEN_API_KEY")
    qwen_api_base: str = Field(
        default="https://dashscope.aliyuncs.com/api/v1",
        env="QWEN_API_BASE"
    )
    qwen_model: str = Field(default="qwen-turbo", env="QWEN_MODEL")
    
    # Claude配置
    claude_api_key: str = Field(default="", env="CLAUDE_API_KEY")
    claude_model: str = Field(default="claude-3-opus-20240229", env="CLAUDE_MODEL")
    
    # 本地向量数据库配置
    vector_db_path: str = Field(
        default="./data/chroma_db",
        env="VECTOR_DB_PATH"
    )
    
    # 嵌入模型配置（使用本地或远程）
    embeddings_provider: Literal["openai", "local"] = Field(
        default="openai",
        env="EMBEDDINGS_PROVIDER"
    )
    # 如果使用本地嵌入模型
    local_embeddings_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="LOCAL_EMBEDDINGS_MODEL"
    )
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(
        default="./logs/education_agent.log",
        env="LOG_FILE"
    )
    
    # 教学配置
    max_conversation_turns: int = 10  # 最大对话轮数
    min_conversation_turns: int = 3   # 最小对话轮数
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()


# 确保必要的目录存在
def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        "./logs",
        "./data",
        "./data/chroma_db",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# 初始化时创建目录
ensure_directories() 