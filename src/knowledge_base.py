"""医学知识库（RAG系统）"""
import os
import glob
from typing import List, Dict
from src.config import config

class MedicalKnowledgeBase:
    """医学知识库 - 基于LangChain的RAG检索"""

    def __init__(self):
        self.knowledge_dir = config.KNOWLEDGE_DIR
        self.vector_db_dir = config.VECTOR_DB_DIR
        self._retriever = None
        self._initialized = False

    def is_ready(self) -> bool:
        return self._initialized and self._retriever is not None

    def initialize(self):
        """初始化知识库"""
        try:
            from langchain_community.document_loaders import DirectoryLoader, TextLoader
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import FAISS

            md_files = glob.glob(os.path.join(self.knowledge_dir, "*.md"))
            txt_files = glob.glob(os.path.join(self.knowledge_dir, "*.txt"))

            all_docs = []
            for pattern in ["*.md", "*.txt"]:
                files = glob.glob(os.path.join(self.knowledge_dir, pattern))
                for f in files:
                    try:
                        with open(f, "r", encoding="utf-8") as fh:
                            content = fh.read()
                        from langchain.schema import Document
                        all_docs.append(Document(
                            page_content=content,
                            metadata={"source": os.path.basename(f)}
                        ))
                    except:
                        pass

            if not all_docs:
                self._initialized = True
                return

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500, chunk_overlap=50
            )
            splits = text_splitter.split_documents(all_docs)

            embeddings = HuggingFaceEmbeddings(
                model_name="shibing624/text2vec-base-chinese",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )

            vectorstore = FAISS.from_documents(splits, embeddings)

            if os.path.exists(self.vector_db_dir):
                vectorstore.save_local(self.vector_db_dir)

            self._retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            self._initialized = True

        except ImportError:
            self._initialized = False
        except Exception:
            self._initialized = False

    def query(self, question: str) -> List[str]:
        """检索相关知识"""
        if not self.is_ready():
            return []
        try:
            docs = self._retriever.invoke(question)
            return [d.page_content for d in docs]
        except:
            return []

    def load_guideline_text(self) -> str:
        """加载内置知识摘要（当知识库未就绪时使用）"""
        return """
## 常见临床指标参考

### 心血管系统
- 正常血压：收缩压 90-120mmHg，舒张压 60-80mmHg
- 正常心率：60-100次/分
- 正常血氧饱和度：95%-100%

### 代谢指标
- 空腹血糖正常值：3.9-6.1 mmol/L
- 糖化血红蛋白正常值：4.0%-6.0%
- 总胆固醇正常值：2.8-5.2 mmol/L
- 甘油三酯正常值：0.56-1.7 mmol/L
- 低密度脂蛋白正常值：<3.4 mmol/L
- 高密度脂蛋白正常值：>1.0 mmol/L

### 身体成分
- 健康BMI范围：18.5-24.0
- 健康体脂率：男性10-20%，女性18-28%

### 睡眠建议
- 成人推荐睡眠时长：7-9小时
- 深睡占比建议：20-25%

### 运动建议
- 成人每周至少150分钟中等强度有氧运动
- 每日步数建议：6000-10000步
"""

knowledge_base = MedicalKnowledgeBase()
