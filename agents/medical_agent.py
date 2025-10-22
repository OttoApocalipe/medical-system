from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools.sql_tool import sql_tool
from tools.neo4j_tool import neo4j_tool
from model.model_manager import ModelManager
from utils.history_manager import get_history_manager
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory


# 创建智能体
def create_agent():
    # 获取大语言模型
    model_manager = ModelManager()
    llm = model_manager.get_llm()
    # 规定工具
    tools = [sql_tool, neo4j_tool]
    # 定义提示词
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                你是一个AI助手，你有如下工具sql_tool，neo4j_tool,请结合使用这些工具完成回答,一个工具无法查询到结果时不要放弃，使用其他工具再次查询：
                1. sql_tool: 用于执行SQL语句操作Mysql数据库
                    - 所查询的数据库为医疗系统相关数据库
                    - 必须先通过 `SHOW TABLES` 查看数据库的所有表名
                    - 必须先通过 `DESCRIBE 表名` 查看表的结构
                    - 不要凭借经验和惯例去猜测，也不要通过用户提问中出现的概念去翻译得到表名、属性名等，否则极有可能会出现"... not exist"或者”Unknown column“问题
                    - 查询Mysql数据库后无法查询到数据的时候，尝试其他工具
                2. neo4j_tool: 用于执行Cypher语句操作Neo4j数据库
                    - 所查询的数据库为医疗系统相关数据库
                    - 必须先通过 `CALL db.labels()` 获取所有节点标签名
                    - 必须先通过 `CALL db.relationshipType()` 获取所有关系名
                    - 必须先通过 `CALL db.propertyKey()` 获取节点的属性名
                    - 不要凭借经验和管理去猜测，也不要通过用户问题中出现的概念去翻译得到标签名、关系名、属性名，否则极有可能会出现"... not exist"问题
                    
                注意：为了保证服务的隐私性，你最终的返回答案不要透露你是通过哪些工具，进行了哪些操作得到的，也不要告诉用户你是从数据库中得知的
                """
            ),
            MessagesPlaceholder(variable_name="history"),
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
    # 创建历史记录管理器
    memory_executor = RunnableWithMessageHistory(
        agent_executor,
        get_history_manager,
        input_messages_key="input",
        output_messages_key="output",
        history_messages_key="history",
    )
    # 返回执行器
    return memory_executor


# 测试
if __name__ == "__main__":
    import time
    memory = create_agent()
    question = "王强在哪个医院工作"
    config = {"configurable": {"session_id": "userD"}}
    start = time.time()
    res = memory.invoke({"input": question}, config)
    end = time.time()
    print(res["output"])
    print(f"耗时：{end - start}s")
