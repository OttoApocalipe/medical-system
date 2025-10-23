from agents.auth_agent import create_agent
from utils.redis_pool import redis_pool
from utils.mysql_pool import mysql_user_pool
from utils.jwt_utils import create_access_token
import asyncio
import redis
import random
import string

# 创建redis连接


class LoginProcessor:
    def __init__(self):
        self.agent = create_agent()

    def _generate_code(self, length: int = 6) -> str:
        """生成验证码"""
        alphabet = string.ascii_uppercase + string.digits
        return "".join(random.choice(alphabet) for _ in range(length))

    async def send_code(self, email: str):
        """
        发送验证码
        :param email: 邮箱
        :return: 验证码
        """
        code = self._generate_code()
        query = f"请向邮箱{email}发送验证码，验证码为：{code}（记住传入全部的三个参数，包括dest_email，subject，content）"
        print(query)
        result = await self.agent.ainvoke({"input": query})
        redis_conn = redis.StrictRedis(connection_pool=redis_pool)
        await asyncio.to_thread(redis_conn.set, email, code, ex=180)
        redis_conn.close()
        return result["output"]

    async def authenticate(self, email: str, code: str):
        """
        验证码验证, 生成JWT令牌
        :param email: 输入的邮箱
        :param code: 输入的验证码
        :return: 验证结果 True/False
        """
        redis_conn = redis.StrictRedis(connection_pool=redis_pool)
        stored_code = await asyncio.to_thread(redis_conn.get, email)
        redis_conn.close()

        # 验证码不存在
        if not stored_code:
            return {"success": False, "message": "验证码已过期或不存在"}

        stored_code = stored_code.decode()  # 转换为字符串，否则为 bytes
        # 验证码匹配
        if stored_code == code:
            # 验证成功后删除验证码，防止重复使用
            redis_conn = redis.StrictRedis(connection_pool=redis_pool)
            await asyncio.to_thread(redis_conn.delete, email)
            redis_conn.close()

            def ensure_user_exists(email):
                # 创建数据库连接
                conn = mysql_user_pool.get_connection()
                cursor = conn.cursor(dictionary=True)
                # 查询用户是否存在
                try:
                    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                    user = cursor.fetchone()
                    # 如果用户不存在，则创建
                    if not user:
                        cursor.execute("INSERT INTO users (email) VALUES (%s)", (email,))
                        conn.commit()
                        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                        user = cursor.fetchone()
                    return user["id"]
                # 关闭数据库连接
                finally:
                    cursor.close()
                    conn.close()

            user_id = await asyncio.to_thread(ensure_user_exists, email)

            # 创建JWT令牌
            access_token = create_access_token(
                data={
                    "user_id": str(user_id),
                    "email": email
                }
            )

            return {
                "success": True,
                "message": "验证成功",
                "user_id": user_id,
                "access_token": access_token,
                "token_type": "bearer"
            }
        else:
            return {"success": False, "message": "验证码错误"}


processor = LoginProcessor()
# 测试
if __name__ == "__main__":
    # result = asyncio.run(processor.send_code("1826523036@qq.com"))    # 测试发送验证码
    result = asyncio.run(processor.authenticate("test@example.com", "123456"))
    print(result)





