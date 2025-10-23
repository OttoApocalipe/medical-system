from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from api_server.schemas.status import ResponseStatus


# ---------- 请求体Schema ----------
# 获取所有会话列表：无需参数（user_id从JWT中获取）
class SessionsListRequest(BaseModel):
    pass


# 创建新会话：user_id从JWT中获取）
class CreateSessionRequest(BaseModel):
    title: Optional[str] = "新对话"  # 可选标题


# ---------- 响应体Schema ----------
class MetaInfo(BaseModel):
    status: ResponseStatus  # 响应状态，如 success 或 error


class SessionItem(BaseModel):
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime


class CreateSessionItem(BaseModel):
    session_id: str
    title: str


# 获取所有会话响应体
class SessionsListResponse(BaseModel):
    meta: MetaInfo
    data: List[SessionItem]


# 创建新会话响应体
class CreateSessionResponse(BaseModel):
    meta: MetaInfo
    data: CreateSessionItem
