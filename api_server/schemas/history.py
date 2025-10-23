from pydantic import BaseModel
from typing import List, Optional, Any
from enum import Enum


# 统一响应状态枚举
class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


# 消息类型枚举
class MessageType(str, Enum):
    HUMAN = "HumanMessage"
    AI = "AIMessage"


# ---------- 请求体Schema ----------
class HistoryRequest(BaseModel):
    session_id: str


# ---------- 响应体Schema ----------
# 单条历史记录
class MessageItem(BaseModel):
    type: MessageType       # 消息类型，如 HumanMessage 或 AIMessage
    content: str    # 消息内容
    metadata: Optional[Any] = None


class MetaInfo(BaseModel):
    status: ResponseStatus     # 响应状态，如 success 或 error
    message: Optional[str] = None


# 响应体
class HistoryResponse(BaseModel):
    meta: MetaInfo
    data: List[MessageItem]



