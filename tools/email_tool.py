from pydantic import BaseModel, Field   # 用于输入参数校验
from langchain.tools import tool    # 用于装饰智能体工具
from fastmcp import Client
from dotenv import load_dotenv
import asyncio
import os

# 加载环境变量
load_dotenv()
mcp_url = os.getenv("MCP_URL")


class EmailArgs(BaseModel):
    # 收件人邮箱：必填
    dest_email: list[str] = Field(..., description="收件人邮箱列表(至少包含一个收件人，必填)", example=["<EMAIL>", "<EMAIL>"])
    # 邮件主题：必填
    subject: str = Field(..., description="邮件主题，必填")
    # 邮件内容：必填
    content: str = Field(..., description="邮件内容，必填")


@tool(args_schema=EmailArgs)
def email_tool(dest_email: list[str], subject: str, content: str) -> str:
    """
    发送邮件，返回结果
    :param dest_email: 收件人邮箱列表(至少包含一个收件人，必填)
    :param subject: 邮件主题(必填)
    :param content: 邮件内容(必填)
    """
    async def run():
        async with Client(mcp_url) as sse:
            res = await sse.call_tool("email_tool", {"dest_email": dest_email, "subject": subject, "content": content})
            return res
    return asyncio.run(run())


