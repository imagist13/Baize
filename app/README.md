# App Package - LangGraph Architecture

这个包使用 LangGraph 重构了原有的代码，提供了模块化、可扩展的架构。

## 架构概览

```
app/
├── __init__.py           # 包初始化
├── config.py             # 配置管理（API keys, 模型设置等）
├── clients.py            # API 客户端管理（OpenAI, Gemini）
├── schemas.py            # Pydantic 数据模型
├── prompts.py            # 系统提示词模板
├── agents.py             # 科普策划与生成代理
├── graph.py              # LangGraph 工作流定义
├── services.py           # 业务逻辑服务层
├── routers.py            # FastAPI 路由
├── tools.py              # 外部工具封装（Tailiy 搜索）
└── main.py               # 应用入口
```

## 核心组件

### 1. Config (`config.py`)
- 集中管理 API keys、base URLs 和模型配置
- 支持环境变量和 credentials.json
- 为不同代理提供默认模型配置

### 2. Clients (`clients.py`)
- `ClientManager`: 统一管理 OpenAI 和 Gemini 客户端
- 自动检测 API key 类型并初始化相应客户端
- 提供客户端就绪状态检查

### 3. Schemas (`schemas.py`)
- `ScienceEducationRequest`: 科普网页生成请求
- `AgentState`: LangGraph 状态模型（记录搜索、策划与生成阶段信息）

### 4. Prompts (`prompts.py`)
- `SCIENCE_PLANNER_PROMPT`: 科普策划提示词
- `SCIENCE_PAGE_GENERATION_PROMPT`: 科普网页生成提示词

### 5. Agents (`agents.py`)
围绕科普网页生产的两个核心代理：
- `SciencePlannerAgent`: 判断是否需要联网检索并生成页面蓝图
- `SciencePageGenerator`: 根据蓝图和检索结果生成最终 HTML

### 6. Graph (`graph.py`)
使用 LangGraph 定义科普网页工作流：
- `create_science_education_graph()`
  - Planner 节点生成提示蓝图
  - 可选 Search 节点调用 Tailiy API
  - Generation 节点产出最终网页

### 7. Services (`services.py`)
`ScienceEducationService` 将工作流封装为易用的服务：
- `generate_science_page()`: 完成策划、检索与页面生成

### 8. Routers (`routers.py`)
FastAPI 路由定义：
- `/generate`: 科普网页生成端点（返回 JSON，包含策划蓝图与 HTML）
- `/`: 主页 UI

### 9. Main (`main.py`)
- `create_app()`: 创建和配置 FastAPI 应用
- 注册中间件和路由
- 挂载静态文件

## LangGraph 工作流示例

### 科普网页流程

```
START
  ↓
Planner 节点
  ↓
{是否需要搜索?}
  ↓ (是)           ↓ (否/失败)
Tailiy 搜索        Generation 节点
  ↓
END
```

### 优势

1. **模块化**: 每个组件职责单一，易于维护
2. **可扩展**: 轻松添加新的代理或工作流节点
3. **可测试**: 每个模块可独立测试
4. **类型安全**: 使用 Pydantic 进行数据验证
5. **编排能力**: LangGraph 提供强大的流程控制

## 使用方法

### 启动应用（新架构）

```bash
python run_new.py
```

或使用 uvicorn：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 配置

在 `credentials.json` 或环境变量中设置：

```json
{
  "API_KEY": "your-api-key",
  "BASE_URL": "https://api.openai.com/v1",
  "MODEL": "gpt-4"
}
```

## 依赖

新增依赖：
- `langgraph`: 工作流编排
- `langchain-core`: LangChain 核心组件

完整依赖见 `requirements.txt`。

## 迁移指南

从旧的 `app.py` 迁移到新架构：

1. **配置**: 配置逻辑移至 `config.py`
2. **客户端**: 客户端管理移至 `clients.py`
3. **数据模型**: Pydantic 模型移至 `schemas.py`
4. **提示词**: 提示词模板移至 `prompts.py`
5. **代理逻辑**: 核心代理移至 `agents.py`
6. **工作流**: LangGraph 流程定义在 `graph.py`
7. **路由**: FastAPI 路由移至 `routers.py`

## 扩展

### 添加新的代理

1. 在 `agents.py` 中定义新的代理类
2. 在 `prompts.py` 中添加提示词
3. 在 `graph.py` 中创建工作流
4. 在 `services.py` 中添加服务方法
5. 在 `routers.py` 中添加路由

### 添加新的工作流节点

```python
async def my_new_node(state: AgentState) -> Dict[str, Any]:
    # 节点逻辑
    return {
        "my_result": "result_data",
        "step": "my_step_complete",
    }

# 在 graph.py 中添加到工作流
workflow.add_node("my_node", my_new_node)
workflow.add_edge("previous_node", "my_node")
```

## 测试

```bash
# 触发科普网页生成流程
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "月食",
    "history": []
  }'
```

## 许可

与项目主仓库相同。

