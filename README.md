# Medical-System 项目报告

## 1. 项目总体架构

### 1.1 前端

使用 **Vue 3** 框架 + **Vite** 构建工具，实现响应式界面和交互逻辑。

### 1.2 后端

- **接口层：** **FastAPI** 定义路由与接口，定义请求体格式，完成前端发送**请求体的处理**和**响应体的返回**
- **业务层：** 封装较为复杂的业务，如**用户登录管理**、**会话管理**、**智能体管理**、**用户数据库操作**等
- **智能体层：** 构建支持 **Runnable** 接口的智能体，在其中**声明智能体可用工具**、**构建 Prompt 提示词**，**实现多轮对话管理**
- **模型层：** 通过懒加载，为智能体提供其需要的大语言模型
- **langchain 工具层：** 创建 **MCP** 客户端，通过 **SSE** 调用 **MCP** 服务端提供的工具，如 **Mysql 关系数据库查询工具**、**Neo4j 图数据库查询工具**、**邮件发送工具**
- **插件层：** 为业务层提供可复用的功能插件，如 **Mysql 连接池**、**Neo4j 连接池**、**Redis 连接池**、**实现 BaseChatMessageHistory 接口的自定义历史消息管理器**

### 1.3 MCP服务端 

封装智能体可调用的工具并注册到 MCP 应用程序，通过 **FastMCP** 提供 **基于SSE** 协议的 **MCP** 服务

### 1.4 数据库

- **Mysql：**
  1. 用于存储系统业务信息，如**用户信息**、**会话信息**。
  2. 作为智能体可查询的知识数据库，存储多种实体的基础信息
- **Neo4j：** 作为知识图谱供智能体查询，提高实体间的关系查询效率
- **Redis：**
  1. 对查询结果进行**缓存**，在用户对同一问题进行频繁提出时，返回缓存结果以减少对模型的推理请求，提高**响应速度**，降低**高并发风险**
  2. 对会话中的消息历史进行管理，用于实现**插件层**的**自定义历史消息管理器**



## 2. API 接口

### 2.1 router-login

#### POST /api/login/send-code

- **作用：** 向用户邮箱发送验证码

- **请求头：**

  Content-Type：application/json

- **请求体：**

  ```json
  {
    "email": "user@example.com"
  }
  ```

- **响应头：**

  Content-Type：application/json

- **响应体：**

  ```json
  {
    "message": "string",
    "email": "user@example.com"
  }
  ```

#### POST /api/login/authenticate

- **作用：** 通过邮箱和验证码验证登录

- **请求头：**

  Content-Type：application/json

- **请求体：**

  ```json
  {
    "email": "user@example.com",
    "code": "string"
  }
  ```

- **响应头：**

  Content-Type：application/json

- **响应体：**

  ```json
  {
    "success": true,
    "message": "string",
    "user_id": 0,
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

### 2.2 router-inference

#### POST /api/inference

- **作用：** 当前登录用户发起查询

- **请求头：**

  Content-Type：application/json

  Authorization：Bearer ${token}

- **请求体：**

  ```json
  {
    "queries": [
      {
        "question": "string",
        "session_id": "string"
      }
    ]
  }
  ```

- **响应头：**

  Content-Type：application/json

- **响应体：**

  ```json
  {
    "meta": {
      "status": "string",
      "timestamp": "2025-10-27T08:11:54.315Z",
      "model": "string",
      "total_queries": 0,
      "from_cache_count": 0,
      "total_time_cost_ms": 0
    },
    "data": [
      {
        "input": "string",
        "output": "string",
        "history": [
          "string"
        ],
        "from_cache": false,
        "time_cost_ms": 0
      }
    ]
  }
  ```

### 2.3 router-history

#### POST /api/history

- **作用： ** 获取当前会话的所有对话历史

- **请求头：**

  Content-Type：application/json

  Authorization：Bearer ${token}

- **请求体：**

  ```JSON
  {
    "session_id": "string"
  }
  ```

- **响应头：**

  Content-Type：application/json

- **响应体：**

  ```json
  {
    "meta": {
      "status": "success",
      "message": "string"
    },
    "data": [
      {
        "type": "HumanMessage",
        "content": "string",
        "metadata": "string"
      }
    ]
  }
  ```



### 2.4 router-sessions

#### POST /api/sessions/list

- **作用：** 获取当前用户的所有会话

- **请求头：**

  Content-Type：application/json

  Authorization：Bearer ${token}

- **请求体：**（传空参，而非不传参）

  ```json
  {}
  ```
  
- **响应头：**

  Content-Type：application/json

- **响应体：**

  ```json
  {
    "meta": {
      "status": "success"
    },
    "data": [
      {
        "session_id": "string",
        "title": "string",
        "created_at": "2025-10-27T08:13:40.171Z",
        "updated_at": "2025-10-27T08:13:40.171Z"
      }
    ]
  }
  ```

#### POST /api/sessions/new

- **作用：** 为当前用户创建新会话

- **请求头：**

  Content-Type：application/json

  Authorization：Bearer ${token}

- **请求体：**

  ```json
  {
    "title": "string"
  }
  ```
  
- **响应头：**

  Content-Type：application/json

- **响应体：**

  ```json
  {
    "meta": {
      "status": "success"
    },
    "data": {
      "session_id": "string",
      "title": "string"
    }
  }
  ```



## 3.  Agent 智能体

### 3.1 medical_agent

医疗对话业务智能体，根据用户的提问或请求回答用户的提问，并完成允许范围内的操作

**可调用工具：**`neo4j_tool`, `mysql_tool`, `email_tool`

**提示词（Prompt）：**

```python
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            你是一个医疗知识智能体，你有如下工具：neo4j_tool, sql_tool, email_tool
            当用户问到医学（包括但不限于疾病、症状等）相关问题时,必须按照如下流程进行使用，
            1. 使用 neo4j_tool 在图数据库中进行查询
                - 所查询的数据库为医学知识相关数据库，包含各种疾病、药物、症状
                - 必须先通过 `CALL db.labels()` 获取所有节点标签名
                - 必须先通过 `CALL db.relationshipType()` 获取所有关系名
                - 必须先通过 `CALL db.propertyKey()` 获取节点的属性名
                - 不要凭借经验和管理去猜测，也不要通过用户问题中出现的概念去翻译得到标签名、关系名、属性名，否则极有可能会出现"... not exist"问题
            2. 当 neo4j 工具无法查询到结果时，用于执行SQL语句查询Mysql数据库
                - 所查询的数据库为医疗系统相关数据库
                - 必须先通过 `SHOW TABLES` 查看数据库的所有表名
                - 必须先通过 `DESCRIBE 表名` 查看表的结构
                - 不要凭借经验和惯例去猜测，也不要通过用户提问中出现的概念去翻译得到表名、属性名等，否则极有可能会出现"... not exist"或者"Unknown column"问题
                - 查询Mysql数据库后无法查询到数据的时候，尝试其他工具
            3. 查询到结果后，对结果进行详适当的阐述和扩展描述，过滤掉明显的错误信息，用尽可能充分的信息返回给用户
            4. 当使用所有查询工具后仍然未能得到用户需要的结果，请返回“我的知识还不足以回答您的问题，请寻求更专业的帮助”
            5. 如果用户还要求发送分析报表，请向用户的邮箱发送你的分析报表，用户邮箱为 {email}, 
            

            注意：
            1. 为了保证服务的隐私性，你最终的返回答案不要透露你是通过哪些工具，进行了哪些操作得到的，也不要告诉用户你是从数据库中得知的
            2. 务必使用查询工具，不要凭借自己的通用知识回答
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
```

### 3.2 auth_agent

邮箱验证智能体，用于用户验证码登陆时向输入邮箱发送验证码

**可调用工具：**`email_tool`

**提示词（Prompt）：**

```python
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
```



## 4. MCP 服务

### 4.1 email_tool

向目标邮箱发送邮件

**:param** dest_email: 收件人邮箱列表（至少包含一个收件人）（必填）

**:param** subject: 邮件主题 （必填）

**:param** content: 邮件内容（必填）



### 4.2 sql_tool

执行SQL查询语句，返回结果

**:param** sql: SQL查询语句



### 4.3 neo4j_tool

执行Cypher查询语句，返回结果

**:param** cypher: Cypher 查询语句



## 5. 数据库

### 5.1 Mysql

- **Database: **
  1. medical_user: 管理用户、会话、相关信息
     - **Table: **
       1. users
       2. sessions
  2. medical_system: 医疗系统知识数据库
     - **Table: **
       1. departments
       2. doctors
       3. exam_records
       4. medical_exams
       5. medical_records
       6. medicines
       7. patient
       8. prescriptions



### 5.2 Redis

| key                     | value               |
| :---------------------- | :------------------ |
| session_id (String)     | 对话历史记录 (JSON) |
| 用户查询哈希值 (String) | AI回答缓存 (String) |



### 5.3 Neo4j

数据来源：[CMKG]([WENGSYX/CMKG: The first Chinese Multimodal Medical Knowledge Graph](https://github.com/WENGSYX/CMKG))

- **Node：**
  1. Category
  2. Department
  3. Disease
  4. Drug
  5. Symptom
- Relationships
  1. BELONGS_TO
  2. HAS_SYMPTOM
  3. RECOMMENDS_DRUG
  4. TREATED_IN



## 6. 部署

通过Dockerfile构建镜像，并通过Docker Compose编排容器

### 6.1 Image: medical-backend

```shell
docker run -d `
--name medical-backend-fastapi `
--env-file env_path `
-p 8000:8000 `
medical-backend
```

### 6.2 Image: fast-mcp

```shell
docker run -d `
--name medical-fast-mcp `
--env-file env_path `
-p 8001:8001 `
fast-mcp
```



## 7. 提交

**前端仓库：** https://github.com/OttoApocalipe/medical-system-frontend.git

**后端（主要业务）仓库：** https://github.com/OttoApocalipe/medical-system.git

**MCP服务仓库：** https://github.com/OttoApocalipe/medical-fast-mcp.git

