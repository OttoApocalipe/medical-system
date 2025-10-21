import redis
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=int(os.getenv("REDIS_DB")),
)

