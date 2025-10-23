from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ---------- 请求体Schema ----------
class SessionsListRequest(BaseModel):
    user_id: int


class CreateSessionRequest(BaseModel):
    user_id: int
    title: Optional[str] = None  # 可选标题


# ---------- 响应体Schema ----------
class MetaInfo(BaseModel):
    status: str  # 响应状态，如 success 或 error


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
