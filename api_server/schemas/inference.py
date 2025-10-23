from pydantic import BaseModel, Field
from typing import List, Any, Optional
from datetime import datetime


# ---------- 请求体Schema ----------
class Query(BaseModel):
    question: str
    session_id: str


class InferenceRequest(BaseModel):
    queries: List[Query]


# ---------- 响应体Schema ----------
# 单条推理结果
class InferenceResult(BaseModel):
    input: str = Field(..., description="输入的问题或请求内容")
    output: str = Field(..., description="模型的回答或输出结果")
    history: List[Any] = Field(default_factory=list, description="当前会话的历史上下文，可为空")
    from_cache: bool = Field(False, description="是否命中缓存")
    time_cost_ms: int = Field(..., description="该条推理耗时（毫秒）")


# 元信息部分
class InferenceMeta(BaseModel):
    status: str = Field(..., description="响应状态，如 success 或 error")
    timestamp: datetime = Field(..., description="响应生成的时间戳")
    model: Optional[str] = Field(None, description="使用的模型名称，如 qwen2.5-72b-instruct")
    total_queries: int = Field(..., description="本次请求包含的查询数量")
    from_cache_count: int = Field(..., description="缓存命中次数")
    total_time_cost_ms: int = Field(..., description="处理整个请求的总耗时（毫秒）")


# 顶层响应结构
class InferenceResponse(BaseModel):
    meta: InferenceMeta
    data: List[InferenceResult]
