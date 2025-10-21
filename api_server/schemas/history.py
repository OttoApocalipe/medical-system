from pydantic import BaseModel


class SessionRequest(BaseModel):
    session_id: str
    