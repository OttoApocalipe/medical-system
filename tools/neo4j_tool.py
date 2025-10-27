from pydantic import BaseModel, Field
from langchain.tools import tool
from fastmcp import Client
from dotenv import load_dotenv
import asyncio
import os

# 加载环境变量
load_dotenv()
mcp_url = os.getenv("MCP_URL")


class Neo4jArgs(BaseModel):
    cypher: str = Field(..., description="Cypher查询语句")


# 定义智能体工具
@tool(args_schema=Neo4jArgs)
def neo4j_tool(cypher: str) -> str:
    """
    执行Cypher查询，返回结果
    :param cypher: Cypher查询语句
    """
    async def run():
        async with Client(mcp_url) as sse:
            res = await sse.call_tool("neo4j_tool", {"cypher": cypher})
            return res
    return asyncio.run(run())


# 测速
if __name__ == "__main__":
    print(neo4j_tool("MATCH (n) RETURN n LIMIT 10"))

