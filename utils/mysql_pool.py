import mysql.connector
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Mysql连接池
mysql_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mysql_pool",
    pool_size=int(os.getenv("MYSQL_POOL_SIZE")),
    host=os.getenv("MYSQL_HOST"),
    port=os.getenv("MYSQL_PORT"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
)
