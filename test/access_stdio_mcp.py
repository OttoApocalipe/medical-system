import asyncio
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters, ClientSession


async def test():
    file_path = "D:\\project\\pycharm\\fast_mcp\\mcp_service\\server_stdio.py"
    # 构建一个命令
    params = StdioServerParameters(
        args=[file_path],
        command=r"D:\venvs\llm\python.exe"
    )
    # 采用异步调用服务器
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化服务器
            print("初始化服务器")
            await session.initialize()
            print("测试MCP服务调用")
            print("=" * 180)
            print("当前服务下的所有工具：")
            tools = await session.list_tools()
            for tool in tools:
                print("*" * 180)
                print(f"工具：{tool}")

if __name__ == '__main__':
    asyncio.run(test())
