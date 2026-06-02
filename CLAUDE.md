# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentKit 是一个基于 LangChain 的智能业务代理系统，支持 RAG 知识库问答和 AIOps 智能运维诊断。使用 FastAPI 作为 Web 框架，LangGraph 实现 Agent 工作流，DashScope（阿里云通义千问）作为 LLM。

## Core Commands

### 服务管理

```bash
# 一键启动所有服务（CLS MCP + Monitor MCP + FastAPI）
uv run python start.py
```

### 依赖管理（使用 uv）

```bash
# 创建虚拟环境并安装依赖
uv venv && uv pip install -e .

# 同步依赖
uv sync
```

### 代码质量

```bash
make format       # 格式化（ruff + black）
make lint         # 代码检查（ruff）
make test         # 运行测试（pytest）
make check-all    # 格式化 + 检查 + 测试
```

## Architecture

### 核心模块 `app/`

- **`api/`** — FastAPI 路由层：chat（RAG 对话）、aiops（故障诊断）、file（文档上传）、health（健康检查）
- **`services/`** — 业务逻辑层：
  - `rag_agent_service.py` — RAG Agent，基于 LangGraph `create_react_agent`，支持流式输出
  - `aiops_service.py` — AIOps 诊断，实现 Plan-Execute-Replan 工作流
  - `vector_store_manager.py` / `vector_index_service.py` — 向量存储管理
  - `document_splitter_service.py` — 文档分块
- **`agent/`** — Agent 核心：
  - `mcp_client.py` — MCP 客户端（全局单例，带重试拦截器）
  - `aiops/` — Plan-Execute-Replan 实现（planner → executor → replanner）
- **`tools/`** — Agent 工具集：知识库检索、Prometheus 告警查询、时间工具
- **`core/`** — 基础组件：LLM 工厂、ChromaDB 客户端
- **`config.py`** — Pydantic Settings 配置管理，从 `.env` 加载

### MCP 服务 `mcp_servers/`

独立的 MCP (Model Context Protocol) 服务，为 AIOps 提供日志查询和监控数据工具：
- `cls_server.py` — 日志查询（端口 8003）
- `monitor_server.py` — 监控数据（端口 8004）

### 前端 `static/`

纯静态 Web 界面（index.html + app.js + styles.css），通过 FastAPI 挂载在 `/static`。

## Key Patterns

- **LLM 集成**：使用 `langchain-qwq` 的 `ChatQwen`，需配置 `DASHSCOPE_API_KEY` 和 `DASHSCOPE_API_BASE` 环境变量
- **Agent 状态**：`AgentState` 使用 `add_messages` 注解实现消息追加；`PlanExecuteState` 使用 `operator.add` 实现步骤历史追加
- **MCP 工具加载**：通过 `get_mcp_client_with_retry()` 获取全局单例客户端，`load_mcp_tools_safe()` 安全加载工具（失败不抛异常）
- **流式输出**：RAG Agent 的 `query_stream()` 使用 SSE (Server-Sent Events) 通过 `sse-starlette` 返回
- **会话管理**：使用 LangGraph 的 `MemorySaver` 作为 checkpointer，`session_id` 即 `thread_id`

## Environment Configuration

通过 `.env` 文件配置，关键变量：
- `DASHSCOPE_API_KEY` — 阿里云 API Key（必填）
- `DASHSCOPE_API_BASE` — API 地址（默认新加坡站点，国内需配置 `https://dashscope.aliyuncs.com/compatible-mode/v1`）
- `DASHSCOPE_MODEL` — 模型名称（默认 `qwen-max`）
- `CHROMA_PERSIST_DIRECTORY` — ChromaDB 持久化目录
- `RAG_TOP_K` — RAG 检索 Top-K
- `CHUNK_MAX_SIZE` / `CHUNK_OVERLAP` — 文档分块参数

## Port Allocation

| 服务 | 端口 |
|------|------|
| FastAPI 主服务 | 9900 |
| CLS MCP 服务 | 8003 |
| Monitor MCP 服务 | 8004 |
