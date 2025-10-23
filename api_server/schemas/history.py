from pydantic import BaseModel
from typing import List, Optional, Any


# ---------- 请求体Schema ----------
class HistoryRequest(BaseModel):
    session_id: str


# ---------- 响应体Schema ----------
# 单条历史记录
class MessageItem(BaseModel):
    type: str       # 消息类型，如 HumanMessage 或 AIMessage
    content: str    # 消息内容
    metadata: Optional[Any]


class MetaInfo(BaseModel):
    status: str     # 响应状态，如 success 或 error


# 响应体
class HistoryResponse(BaseModel):
    meta: MetaInfo
    data: List[MessageItem]



