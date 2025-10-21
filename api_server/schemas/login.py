from pydantic import BaseModel, EmailStr


class SendCodeRequest(BaseModel):
    email: EmailStr


class AuthRequest(BaseModel):
    email: EmailStr
    code: str
    