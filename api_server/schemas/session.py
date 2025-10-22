from pydantic import BaseModel
from typing import Optional


class UserRequest(BaseModel):
    user_id: int


class CreateSessionRequest(BaseModel):
    user_id: int
    title: Optional[str] = None  # 可选标题