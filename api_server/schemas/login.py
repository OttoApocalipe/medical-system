from pydantic import BaseModel, EmailStr


# ---------- 请求体Schema ----------
class SendCodeRequest(BaseModel):
    email: EmailStr


class AuthRequest(BaseModel):
    email: EmailStr
    code: str


# ---------- 响应体Schema ----------
class SendCodeResponse(BaseModel):
    message: str
    email: EmailStr


class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: int
