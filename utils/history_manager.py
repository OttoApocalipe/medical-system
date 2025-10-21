from typing import List, Dict
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain.schema import HumanMessage, AIMessage
from dotenv import load_dotenv
import redis
import json
import os

# 加载环境变量
load_dotenv()

# 创建redis连接
redis_conn = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=int(os.getenv("REDIS_DB")),
)


# 创建历史记录管理类
class HistoryManager(BaseChatMessageHistory):
    def __init__(self, session_id: str):
        self.session_id = session_id

    def _serialize_message(self, message: BaseMessage) -> Dict:
        """
        将消息对象序列化为python字典
        :param message: 消息对象
        :return: 序列化后的字典
        """
        return {
            "type": message.__class__.__name__,
            "content": message.content,
            "metadata": message.metadata if hasattr(message, "metadata") else None,
        }

    def _deserialize_message(self, message_dict: Dict) -> BaseMessage:
        """
        将python字典反序列化为消息对象
        :param message_dict: python字典
        :return: 反序列化后的消息对象
        """
        message_type = message_dict["type"]
        if message_type == "HumanMessage":
            return HumanMessage(
                content=message_dict["content"],
                metadata=message_dict["metadata"],
            )
        elif message_type == "AIMessage":
            return AIMessage(
                content=message_dict["content"],
                metadata=message_dict["metadata"]
            )
        else:
            raise ValueError(f"Invalid message type: {message_type}")

    @property
    def messages(self) -> List[BaseMessage]:
        # 判断redis是否有该会话的记录
        history_json = redis_conn.get(self.session_id)
        if not history_json:
            return []
        history_dict = json.loads(history_json.decode())
        # 返回反序列化后的消息列表
        return [self._deserialize_message(message_dict) for message_dict in history_dict]

    def add_messages(self, messages: List[BaseMessage]) -> None:
        current_history = self.messages
        current_history.extend(messages)
        # 将消息列表序列化为json字符串
        history_json = [self._serialize_message(message) for message in current_history]
        redis_conn.set(self.session_id, json.dumps(history_json))

    def clear(self) -> None:
        redis_conn.delete(self.session_id)


# 获取会话历史（会话存储器）
def get_history_manager(session_id: str) -> HistoryManager:
    return HistoryManager(session_id)



