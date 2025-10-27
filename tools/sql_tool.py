from pydantic import BaseModel, Field   # 用于输入参数校验
from langchain.tools import tool    # 用于装饰智能体工具
from fastmcp import Client
from dotenv import load_dotenv
import asyncio
import os

# 加载环境变量
load_dotenv()
mcp_url = os.getenv("MCP_URL")


# 参数校验类
class SqlArgs(BaseModel):
    sql: str = Field(..., description="SQL查询语句 (或者Mysql的辅助语句如: SHOW, DESCRIBE)")


# 定义智能体工具
@tool(args_schema=SqlArgs)
def sql_tool(sql: str) -> str:
    """
    执行SQL查询语句，返回结果
    :param sql: SQL查询语句 (或者Mysql的辅助语句如: SHOW, DESCRIBE)
    """
    async def run():
        async with Client(mcp_url) as sse:
            res = await sse.call_tool("sql_tool", {"sql": sql})
            return res
    return asyncio.run(run())


# 测试
if __name__ == "__main__":
    print(sql_tool("SHOW TABLES"))

