from agents.medical_agent import create_agent
from pydantic import BaseModel
from typing import List, AsyncGenerator
from concurrent.futures import ThreadPoolExecutor   # 线程池
from utils.redis_pool import redis_pool
from utils.mysql_pool import mysql_user_pool
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

    async def sync_get_user_email(self, session_id: str) -> str:
        """
        根据会话ID获取用户邮箱
        :param session_id: 会话UUID
        :return: 用户邮箱（若查询失败返回空字符串）
        """
        def sync_get_email():
            conn = None
            cursor = None
            try:
                conn = mysql_user_pool.get_connection()
                cursor = conn.cursor(dictionary=True)

                # 查询会话关联的user_id
                cursor.execute("""
                    SELECT user_id FROM sessions
                    WHERE session_uuid = %s
                    LIMIT 1
                """, (session_id,))
                user_id = cursor.fetchone()["user_id"]

                # 查询用户邮箱
                cursor.execute("""
                    SELECT email FROM users
                    WHERE id = %s
                    LIMIT 1
                """, (user_id,))
                email = cursor.fetchone()["email"]
                return email
            except Exception as e:
                print(f"数据库查询失败: {str(e)}")
                return "无"
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

        # 创建线程并执行同步函数
        return await asyncio.to_thread(sync_get_email)

    # 会话归属验证
    async def _verify_session_owner(self, user_id: int, session_id: str) -> dict:
        """
        验证会话是否属于当前用
        :param user_id: 用户ID
        :param session_id: 会话ID
        :return: {"success": bool, "message": str}
        """
        def sync_verify():
            """
            同步Mysql查询(避免阻塞时间循环)
            """
            conn = mysql_user_pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            try:
                # 查session表：session_uuid是否关联当前user_id
                cursor.execute("""
                    SELECT 1 FROM sessions
                    WHERE session_uuid = %s AND user_id = %s
                """, (session_id, user_id))
                if cursor.fetchone():
                    return {"success": True, "message": "会话归属验证通过"}
                else:
                    return {"success": False, "message": "会话不属于当前用户"}
            except Exception as e:
                # 捕获Mysql异常，返回错误信息
                return {"success": False, "message": f"数据库查询失败: {str(e)}"}
            finally:
                cursor.close()
                conn.close()

        return await asyncio.to_thread(sync_verify)

    async def check_session_owner(self, user_id: int, session_id: str) -> dict:
        """
        公开方法
        :param user_id: 用户ID
        :param session_id: 会话ID
        :return: {"success": bool, "message": str}
        """
        return await self._verify_session_owner(user_id, session_id)

    def _inference(self, query: Query):
        config = {"configurable": {"session_id": query.session_id}}
        result = self.agent.invoke({"input": query.question}, config)
        return result

    # 异步推理
    async def _inference_async(self, query: Query):
        config = {"configurable": {"session_id": query.session_id}}
        email = await self.sync_get_user_email(query.session_id)
        print("用户邮箱", email)
        result = await self.agent.ainvoke({"input": query.question, "email": email}, config)
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


processor = InferenceProcessor()


