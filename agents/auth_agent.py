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
                你是一个AI助手，需使用`email_tool`向指定邮箱发送验证码，严格遵循以下规则：
                1. 调用`email_tool`时，必须传入三个必填参数，缺一不可：
                   - `dest_email`：收件人邮箱列表（如[xxx@qq.com]）；
                   - `subject`：固定为“Medical Mind 验证消息”；
                   - `content`：格式为“【Medical Mind】登录验证码：{{具体验证码}}，3分钟内有效。工作人员不会向您索要验证码，切勿将验证码提供给他人，谨防被骗”
                2. 最终返回你用该工具发送的邮件的content中的{{具体验证码}}部分，不要反悔其他任何内容，如：
                    QKI02Q
                    1Z3JKL
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


