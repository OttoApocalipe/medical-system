from agents.medical_agent import create_agent
from pydantic import BaseModel
from typing import List, AsyncGenerator
from concurrent.futures import ThreadPoolExecutor   # 线程池
from utils.redis_pool import redis_pool
from api_server.schemas.inference import Query
import hashlib
import asyncio
import redis
import json
import os
import time


# 创建redis连接
redis_conn = redis.StrictRedis(connection_pool=redis_pool)


# class InferenceProcessor:
#     def __init__(self):
#         self.agent = create_agent()
#
#     def _inference(self, query: Query):
#         config = {
#             "configurable":
#                 {"session_id": query.session_id}
#         }
#         result = self.agent.invoke({"input": query.question}, config)
#         return result
#
#     def inference_with_cache(self, query: Query):
#         start_time = time.time()
#         # 设置 key，保证唯一性
#         hash_num = hashlib.sha256(query.question.encode()).hexdigest()
#         key = f"{query.session_id}:{hash_num}"
#
#         # 尝试从缓存读取
#         cache = redis_conn.get(key)
#         if cache:
#             redis_conn.expire(key, 180)
#             print("缓存命中")
#             result = json.loads(cache.decode())
#             result["from_cache"] = True
#         else:
#             print("缓存未命中")
#             raw_result = self._inference(query)
#
#             # 只取可序列化内容，例如 output 文本
#             result = {
#                 "input": query.question,
#                 "output": getattr(raw_result, "output", str(raw_result)),
#                 "history": getattr(raw_result, "history", []),
#                 "from_cache": False,
#             }
#
#             redis_conn.set(key, json.dumps(result), ex=180)
#
#         # 计算时间
#         end_time = time.time()
#         result["time_cost_ms"] = int((end_time - start_time) * 1000)
#
#         return result
#
#     def process_parallel_requests(self, queries: List[Query]):
#         with ThreadPoolExecutor(max_workers=min(5, len(queries))) as executor:
#             results = executor.map(self.inference_with_cache, queries)
#             return list(results)


class InferenceProcessor:
    def __init__(self):
        self.agent = create_agent()

    def _inference(self, query: Query):
        config = {"configurable": {"session_id": query.session_id}}
        result = self.agent.invoke({"input": query.question}, config)
        return result

    # 异步推理
    async def _inference_async(self, query: Query):
        config = {"configurable": {"session_id": query.session_id}}
        result = await self.agent.ainvoke({"input": query.question}, config)
        return result

    async def inference_with_cache_async(self, query: Query):
        start_time = time.time()
        # 构建唯一 key
        hash_num = hashlib.sha256(query.question.encode()).hexdigest()
        key = f"{query.session_id}:{hash_num}"

        # 尝试从缓存中读取
        cache = await asyncio.to_thread(lambda: redis_conn.get(key))
        if cache:
            await asyncio.to_thread(lambda: redis_conn.expire(key, 180))
            print("缓存命中")
            result = json.loads(cache.decode())
            result["from_cache"] = True
        else:
            print("缓存未命中")
            raw_result = await self._inference_async(query)
            print("返回数据类型", type(raw_result))
            print("返回数据", raw_result)
            result = {
                "input": query.question,
                "output": raw_result.get("output"),
                "history": getattr(raw_result, "history", []),
                "from_cache": False,
            }
            await asyncio.to_thread(redis_conn.set, key, json.dumps(result), ex=180)

        end_time = time.time()
        result["time_cost_ms"] = int((end_time - start_time) * 1000)
        return result

    # 保留同步接口（兼容旧版本）
    def inference_with_cache(self, query: Query):
        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(self.inference_with_cache_async(query))
        except RuntimeError:
            return asyncio.run(self.inference_with_cache_async(query))

    async def stream(self, query: Query) -> AsyncGenerator[dict, None]:
        start_time = time.time()
        hash_num = hashlib.sha256(query.question.encode()).hexdigest()
        key = f"{query.session_id}:{hash_num}"

        # 检查缓存
        cache = await asyncio.to_thread(redis_conn.get, key)
        if cache:
            await asyncio.to_thread(lambda: redis_conn.expire(key, 180))
            cached_result = json.loads(cache.decode())
            cached_result["from_cache"] = True
            yield cached_result
            return

        # 流式推理
        generated_texts = []
        async for chunk in self.agent.astream(
                {"input": query.question},
                {"configurable": {"session_id": query.session_id}}
        ):
            text = getattr(chunk, "content", None) or getattr(chunk, "output", None) or str(chunk)
            if text:
                generated_texts.append(text)
                yield {"chunk": text}

        # 缓存完整结果
        result = {
            "input": query.question,
            "output": "".join(generated_texts),
            "history": [],
            "from_cache": False,
            "time_cost_ms": int((time.time() - start_time) * 1000)
        }
        await asyncio.to_thread(lambda: redis_conn.set(key, json.dumps(result), ex=180))


processor = InferenceProcessor()






