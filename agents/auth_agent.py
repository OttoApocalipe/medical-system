from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools.email_tool import email_tool
from model.model_manager import ModelManager
from utils.history_manager import get_history_manager
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_agent():
    # 获取大语言模型
    model_manager = ModelManager()
    llm = model_manager.get_llm()
    # 规定工具
    tools = [email_tool]
    # 创建提示词
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                你是一个AI助手，有如下工具
                1. email_tool: 向指定邮箱发送发送邮件验证码
                - 验证码为6位，由数字和大写字母组成，由你随机生成，尽可能不要是有规律的
                - 邮件标题为：“Medical Mind 验证消息”
                - 邮件内容示例如下（验证码部分不要照抄）：
                    【Medical Mind】登录验证码：ZCE7ZC，3分钟内有效。工作人员不会向您索要验证码，切勿将验证码提供给他人，谨防被骗
                    【Medical Mind】登录验证码：7HCK23，3分钟内有效。工作人员不会向您索要验证码，切勿将验证码提供给他人，谨防被骗
                - 只返回你发送的验证码，其他内容都不要返回(包括你的提示信息)：如
                    AKZ23Z
                    8ZKC34
                """,
            ),
            (
                "human",
                "{input}"
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    # 创建智能体
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )
    # 创建智能体执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
    )
    # 返回执行器
    return agent_executor


# 测试
if __name__ == "__main__":
    agent = create_agent()
    question = "请向邮箱1826523036@qq.com发送验证码"
    res = agent.invoke({"input": question})
    print(res["output"])


