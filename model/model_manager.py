from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()


# 创建用于管理模型的类
class ModelManager:
    # 类属性：大语言模型
    _llm = None
    # 类属性：词嵌入模型
    _embedding = None

    def __init__(self):
        # 获取大语言模型名称
        self.model_name = os.getenv("LLM_MODEL_NAME")
        # 获取词嵌入模型路径
        self.embedding_model_path = os.getenv("EMBEDDING_MODEL_PATH")

    # 加载大语言模型
    def get_llm(self):
        # 懒加载机制
        if self._llm is None:
            self._llm = ChatOpenAI(model_name=self.model_name)
        return self._llm

    # 加载词嵌入模型
    def get_embedding(self):
        # 懒加载机制
        if self._embedding is None:
            self._embedding = HuggingFaceEmbeddings(model_name=self.embedding_model_path)
        return self._embedding


