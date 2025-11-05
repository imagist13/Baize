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
├── agents.py             # 智能代理实现
├── graph.py              # LangGraph 工作流定义
├── services.py           # 业务逻辑服务层
├── routers.py            # FastAPI 路由
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
- `ChatRequest`: 聊天/生成请求
- `PlanningRequest`: 页面规划请求
- `CodePlanningRequest`: 代码规划请求
- `CombinedPlanningRequest`: 组合规划请求
- `AgentState`: LangGraph 状态模型

### 4. Prompts (`prompts.py`)
- `ANIMATION_GENERATION_PROMPT`: 动画生成提示词
- `CODE_PLANNING_PROMPT`: 代码规划提示词
- `PAGE_PLANNING_PROMPT`: 页面规划提示词

### 5. Agents (`agents.py`)
三个专门的智能代理：
- `AnimationGenerationAgent`: 生成交互式动画 HTML
- `CodePlanningAgent`: 生成代码架构规划
- `PagePlanningAgent`: 生成页面布局规划

### 6. Graph (`graph.py`)
使用 LangGraph 定义工作流：
- `create_code_planning_graph()`: 独立代码规划流程
- `create_page_planning_graph()`: 独立页面规划流程
- `create_combined_planning_graph()`: 组合规划流程
  - 先执行代码规划
  - 将代码规划结果传递给页面规划
  - 支持条件边和错误处理

### 7. Services (`services.py`)
`PlanningService` 提供高层业务逻辑：
- `execute_code_planning()`: 执行代码规划
- `execute_page_planning()`: 执行页面规划
- `execute_combined_planning()`: 执行组合规划

### 8. Routers (`routers.py`)
FastAPI 路由定义：
- `/code/plan`: 代码规划端点
- `/plan`: 页面规划端点
- `/plan/combined`: 组合规划端点
- `/generate`: 动画生成端点（SSE 流式）
- `/`: 主页 UI

### 9. Main (`main.py`)
- `create_app()`: 创建和配置 FastAPI 应用
- 注册中间件和路由
- 挂载静态文件

## LangGraph 工作流示例

### 组合规划流程

```
START
  ↓
[Code Planning Node]
  ↓
{Should Continue?}
  ↓ (yes)          ↓ (error)
[Page Planning]    END
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

### 启动应用（旧架构）

```bash
python app.py
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
# 测试代码规划
curl -X POST http://localhost:8000/code/plan \
  -H "Content-Type: application/json" \
  -d '{"problem": "实现一个分布式缓存系统"}'

# 测试页面规划
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{"topic": "冒泡排序可视化"}'

# 测试组合规划
curl -X POST http://localhost:8000/plan/combined \
  -H "Content-Type: application/json" \
  -d '{
    "code_plan": {"problem": "实现排序算法"},
    "page_plan": {"topic": "排序算法可视化"}
  }'
```

## 许可

与项目主仓库相同。

