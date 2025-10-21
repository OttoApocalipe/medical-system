from pydantic import BaseModel
from typing import List


class Query(BaseModel):
    question: str
    session_id: str


class InferenceRequest(BaseModel):
    queries: List[Query]
