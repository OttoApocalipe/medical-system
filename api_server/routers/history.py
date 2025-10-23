from fastapi import APIRouter
import redis
import json
from utils.redis_pool import redis_pool
from api_server.schemas.history import HistoryRequest, HistoryResponse

router = APIRouter(prefix="/api", tags=["history"])


@router.post("/history", response_model=HistoryResponse)
async def get_history(request: HistoryRequest):
    redis_conn = redis.StrictRedis(connection_pool=redis_pool)
    history_json = redis_conn.get(request.session_id)
    if not history_json:
        return {"meta": {"status": "success"}, "data": []}
    history_list = json.loads(history_json.decode())
    return {"meta": {"status": "success"}, "data": history_list}