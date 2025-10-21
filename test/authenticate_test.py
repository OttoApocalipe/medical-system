from utils.redis_pool import redis_pool
import redis

redis_conn = redis.StrictRedis(connection_pool=redis_pool)

res = redis_conn.get("1826523036@qq.com")
print(res.decode())