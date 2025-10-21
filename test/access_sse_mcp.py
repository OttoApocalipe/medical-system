from fastmcp import Client
import asyncio


# 定义一个异步函数
async def test():
    # 调用mcp服务器
    async with Client("http://localhost:8001/sse") as sse:
        print("测试MCP服务调用")
        print("=" * 180)
        print("=" * 180)
        print("当前服务下的所有工具：")
        tools = await sse.list_tools()
        for tool in tools:
            print("*" * 180)
            print(f"工具名称：{tool.name}")
            print(f"工具描述：{tool.description}")
            print(f"工具参数：{tool.inputSchema}")
            print(f"工具返回：{tool.outputSchema}")
        print("=" * 180)
        print("=" * 180)
        print("测试工具调用")
        print("*" * 180)
        print("工具名称：sql_tool")
        res1 = await sse.call_tool("sql_tool", {"sql": "SHOW TABLES"})
        print(res1)
        print("*" * 180)
        print("工具名称：neo4j_tool")
        res2 = await sse.call_tool("neo4j_tool", {"cypher": "MATCH (n) RETURN n LIMIT 10"})
        print(res2)


if __name__ == '__main__':
    asyncio.run(test())
