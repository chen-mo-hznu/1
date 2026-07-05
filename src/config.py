import os, tempfile
from dotenv import load_dotenv
load_dotenv()

class Config:
    LLM_API_KEY = os.environ.get('LLM_API_KEY') or 'your_api_key_here'
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL') or 'https://api.llm.ustc.edu.cn/v1'
    LLM_MODEL = os.environ.get('LLM_MODEL') or 'qwen3.5'
    DB_PATH = os.path.join(tempfile.gettempdir(), 'ha_db', 'health.db')
    KNOWLEDGE_DIR = os.path.join(tempfile.gettempdir(), 'ha_db', 'knowledge')

config = Config()
