from utils.redis_pool import redis_pool
from utils.mysql_pool import mysql_user_pool
from api_server.schemas.status import ResponseStatus
import asyncio
import redis
import json


class HistoryProcessor:
    def __init__(self):
        pass

    async def _verify_session_owner(self, user_id: int, session_id: str) -> dict:
        """
        验证会话是否属于当前用户
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

    async def _get_history_from_redis(self, session_id: str) -> dict:
        """
        从Redis中获取历史记录
        :param session_id: 会话ID
        :return: {"success": bool, "data": list, "message": str}
        """
        def sync_get_history():
            """
            同步Redis操作
            """
            redis_conn = redis.StrictRedis(connection_pool=redis_pool)
            try:
                history_json = redis_conn.get(session_id)
                if not history_json:
                    return {"success": True, "data": [], "message": "无历史记录"}
                # 解析JSON
                history_list = json.loads(history_json.decode())
                return {"success": True, "data": history_list, "message": "获取历史记录成功"}
            except Exception as e:
                # 捕获Redis异常，返回错误信息
                return {"success": False, "data": [], "message": f"Redis操作失败: {str(e)}"}
            finally:
                redis_conn.close()

        return await asyncio.to_thread(sync_get_history)

    async def get_history(self, user_id: int, session_id: str) -> dict:
        """
        获取历史记录
        :param session_id: 会话ID
        :param user_id: 用户ID
        :return: {"success": bool, "data": list, "message": str, "status": ResponseStatus}
        """
        # 验证会话是否属于当前用户
        owner_verify_result = await self._verify_session_owner(user_id, session_id)
        if not owner_verify_result["success"]:
            return {
                "success": False,
                "data": [],
                "message": owner_verify_result["message"],
                "status": ResponseStatus.ERROR
            }

        # 从Redis中获取历史记录
        redis_result = await self._get_history_from_redis(session_id)
        if not redis_result["success"]:
            return {
                "success": False,
                "data": [],
                "message": redis_result["message"],
                "status": ResponseStatus.ERROR
            }

        # 响应成功
        return {
            "success": True,
            "data": redis_result["data"],
            "message": redis_result["message"],
            "status": ResponseStatus.SUCCESS
        }


# 示例化Processor
processor = HistoryProcessor()

