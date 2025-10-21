from agents.auth_agent import create_agent
from utils.redis_pool import redis_pool
from utils.mysql_pool import mysql_pool
import asyncio
import redis

# 创建redis连接
redis_conn = redis.StrictRedis(connection_pool=redis_pool)


class LoginProcessor:
    def __init__(self):
        self.agent = create_agent()

    async def send_code(self, email: str):
        """
        发送验证码
        :param email: 邮箱
        :return: 验证码
        """
        query = f"请向邮箱{email}发送验证码"
        result = await self.agent.ainvoke({"input": query})
        await asyncio.to_thread(redis_conn.set, email, str(result["output"]), ex=180)
        return result["output"]

    async def authenticate(self, email: str, code: str):
        """
        验证码验证
        :param email: 输入的邮箱
        :param code: 输入的验证码
        :return: 验证结果 True/False
        """
        stored_code = await asyncio.to_thread(redis_conn.get, email)
        print(f"Redis中存的验证码: {stored_code}")
        if not stored_code:
            return {"success": False, "message": "验证码已过期或不存在"}

        stored_code = stored_code.decode()  # 转换为字符串，否则为 bytes
        if stored_code == code:
            # 验证成功后删除验证码，防止重复使用
            await asyncio.to_thread(redis_conn.delete, email)

            def ensure_user_exists(email):
                # 创建数据库连接
                conn = mysql_pool.get_connection()
                cursor = conn.cursor()
                # 查询用户是否存在
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                if not user:
                    cursor.execute("INSERT INTO user (email) VALUES (%s)", (email,))
                    conn.commit()
                # 关闭数据库连接
                cursor.close()
                conn.close()

            asyncio.to_thread(ensure_user_exists, email)

            return {"success": True, "message": "验证成功"}
        else:
            return {"success": False, "message": "验证码错误"}


processor = LoginProcessor()
# 测试
if __name__ == "__main__":
    result = asyncio.run(processor.send_code("1826523036@qq.com"))
    print(result)





