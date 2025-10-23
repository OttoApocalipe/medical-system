from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from service.inference import processor as inference_processor
from api_server.schemas.inference import InferenceRequest, InferenceResponse
from api_server.dependencies import get_current_user
import asyncio
import time
import os

router = APIRouter(prefix="/api", tags=["inference"])


@router.post("/inference", response_model=InferenceResponse)
async def inference(
        request: InferenceRequest,
        current_user: dict = Depends(get_current_user)
):
    # 从鉴权依赖中获取user_id
    user_id = current_user["user_id"]

    # 批量验证每个query的会话归属（逐个检查，避免越权访问）
    for query in request.queries:
        verify_result = await inference_processor.check_session_owner(user_id, query.session_id)
        if not verify_result["success"]:
            # 403 Forbidden
            if "会话不属于当前用户" in verify_result["message"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无权访问会话「{query.session_id}」:{verify_result['message']}"
                )
            else:
                # 500 Internal Server Error
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"会话归属验证失败:{verify_result['message']}"
                )

    start_time = time.time()
    tasks = [inference_processor.inference_with_cache_async(query) for query in request.queries]
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
