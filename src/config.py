import os

class Config:
    try:
        import streamlit as st
        LLM_API_KEY = st.secrets.get("LLM_API_KEY", "")
        LLM_BASE_URL = st.secrets.get("LLM_BASE_URL", "")
        LLM_MODEL = st.secrets.get("LLM_MODEL", "qwen3.5")
    except ImportError:
        from dotenv import load_dotenv
        load_dotenv()
        LLM_API_KEY = os.getenv("LLM_API_KEY", "your_api_key_here")
        LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.llm.ustc.edu.cn/v1")
        LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.5")

    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_data", "health.db")
    KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "medical_knowledge")
    VECTOR_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_data", "vector_db")
    EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "exports")

config = Config()
