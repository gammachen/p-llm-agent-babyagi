# BabyAGI Agent

基于 BabyAGI 框架开发的自主 Agent 系统，具备任务规划、工具执行和自主学习能力。

## 功能特性

- 自主任务规划和执行
- 多种大语言模型支持 (OpenAI, Ollama)
- 向量数据库集成 (ChromaDB)
- 工具调用能力 (命令执行、文件读写、网络搜索等)
- RESTful API 接口
- Web 可视化界面
- 容器化部署支持
- 详细的日志记录和监控

## 快速开始

### 环境准备

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件:

```env
# LLM 配置
LLM_PROVIDER=openai  # openai, ollama
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# Ollama 配置（如果使用 Ollama）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# 向量数据库配置
VECTOR_DB=chroma
CHROMA_PERSIST_DIR=./chroma_db

# 任务配置
MAX_ITERATIONS=5
OBJECTIVE=Develop a task list

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=babyagi.log

# LLM 调用配置
LLM_TIMEOUT=120
LLM_RETRY_ATTEMPTS=3
```

### 运行方式

#### 1. 命令行模式

```bash
# 使用默认配置运行
python main.py

# 指定目标和初始任务
python main.py --objective "Solve world hunger" --initial-task "Research causes of hunger"

# 指定其他参数
python main.py --objective "Write a novel" --max-iterations 10
```

#### 2. API 模式

```bash
# 启动 API 服务
python main.py --mode api

# 或者直接运行
python api/app.py
```

API 端点:
- `POST /api/run` - 运行 BabyAGI 任务
- `GET /api/tasks` - 获取任务历史
- `GET /health` - 健康检查

#### 3. Web 界面模式

```bash
# 启动 Web 界面
python main.py --mode web

# 或者直接运行
python web/interface.py
```

访问 `http://localhost:7860` 使用 Web 界面。

## 日志系统

本系统具有全面的日志记录功能，可以帮助您监控和调试系统运行情况：

- **详细级别**：支持 ERROR, WARNING, INFO, DEBUG 四个日志级别
- **多输出**：日志同时输出到控制台和文件
- **内容覆盖**：
  - LLM 调用（模型、提示词、响应、执行时间等）
  - 工具执行（工具名称、参数、执行结果等）
  - 任务执行流程（任务创建、优先级排序等）
  - API 请求响应（请求参数、响应结果等）
  - 系统运行状态（启动、完成、错误等）

日志文件默认保存为 `babyagi.log`，可以通过 `LOG_FILE` 环境变量配置。

## Docker 部署

```bash
# 构建镜像
docker build -t babyagi-agent .

# 运行容器
docker run -d \
  -p 5000:5000 \
  -p 7860:7860 \
  -e OPENAI_API_KEY=your_api_key \
  --name babyagi-agent \
  babyagi-agent

# 或使用 docker-compose
docker-compose up -d
```

## 项目结构

```
babyagi-agent/
├── config/              # 配置文件
├── core/                # 核心逻辑
├── tools/               # 工具集
├── api/                 # API服务
├── web/                 # Web界面
├── tests/               # 测试文件
├── main.py             # 主入口
├── requirements.txt    # 依赖列表
├── Dockerfile          # Docker配置
└── docker-compose.yml  # 容器编排
```

## 配置说明

### LLM Providers

1. **OpenAI**
   - 设置 `LLM_PROVIDER=openai`
   - 配置 `OPENAI_API_KEY` 和 `OPENAI_MODEL`

2. **Ollama**
   - 设置 `LLM_PROVIDER=ollama`
   - 配置 `OLLAMA_BASE_URL` 和 `OLLAMA_MODEL`

### 向量数据库

当前支持 ChromaDB，未来可扩展支持 Pinecone、Weaviate 等。

## 开发指南

### 添加新工具

在 `tools/tools.py` 中添加工具函数，并注册到 `TOOL_REGISTRY`。

### 扩展功能

- 实现多 Agent 协作
- 增强长期记忆管理
- 添加更多 LLM 提供商支持
- 实现更复杂的任务规划算法

## 许可证

MIT License