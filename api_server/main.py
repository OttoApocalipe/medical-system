import redis
from fastapi import FastAPI, Query as FastAPIQuery, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List
from service.inference import InferenceProcessor, Query
from utils.history_manager import get_history_manager
from utils.redis_pool import redis_pool
from service.login import processor as login_processor
from datetime import datetime
import os
import time
import json
from dotenv import load_dotenv
import asyncio

load_dotenv()

app = FastAPI(title="Medical System", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = InferenceProcessor()


# 请求体
class InferenceRequest(BaseModel):
    queries: List[Query]


# 邮箱验证码请求体
class SendCodeRequest(BaseModel):
    email: EmailStr  # 自动验证邮箱格式


# 邮箱验证请求体
class AuthRequest(BaseModel):
    email: EmailStr
    code: str


# ---------------------------
# 非流式推理接口
# ---------------------------
@app.post("/api/inference")
async def inference(request: InferenceRequest):
    start_time = time.time()
    tasks = [processor.inference_with_cache_async(query) for query in request.queries]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    from_cache_count = sum(1 for result in results if result.get("from_cache"))
    return {
        "meta": {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "model": os.getenv("LLM_MODEL_NAME"),
            "total_queries": len(results),
            "from_cache_count": from_cache_count,
            "total_time_cost_ms": int((end_time - start_time) * 1000),
        },
        "data": results,
    }


# ---------------------------
# 获取历史消息接口
# ---------------------------
@app.get("/api/history")
async def get_history(session_id: str):
    redis_conn = redis.StrictRedis(connection_pool=redis_pool)
    history_json = redis_conn.get(session_id)
    if not history_json:
        return {"meta": {"status": "success"}, "data": []}
    history_list = json.loads(history_json.decode())
    return {"meta": {"status": "success"}, "data": history_list}


@app.post("/api/login/send-code", status_code=status.HTTP_201_CREATED)
async def send_code(req: SendCodeRequest):
    try:
        code = await login_processor.send_code(req.email)
        return {"message": "验证码已发送", "email": req.email}
    except ValueError as e:
        # 自定义异常，如邮箱不合法、发送失败
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=503, detail="邮件服务暂不可用")


@app.post("/api/login/authenticate", status_code=status.HTTP_200_OK)
async def authenticate(req: AuthRequest):
    """
    验证用户邮箱验证码
    """
    result = await login_processor.authenticate(req.email, req.code)

    if result["success"]:
        return result
    else:
        # 验证码错误或过期返回 400
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])


@app.get("api/chat/sessions")
async def get_sessions(user_id: id):
    """
    获取会话列表
    """
    redis_conn = redis.StrictRedis(connection_pool=redis_pool)
    sessions = redis_conn.smembers("sessions")
    sessions = [session.decode() for session in sessions]
    return {"meta": {"status": "success"}, "data": sessions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


