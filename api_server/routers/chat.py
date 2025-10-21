from fastapi import APIRouter
import asyncio
import time
import os
from datetime import datetime
from service.inference import processor
from api_server.schemas.chat import InferenceRequest

router = APIRouter(prefix="/api", tags=["inference"])


@router.post("/inference")
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