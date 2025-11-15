# 魔搭创空间部署指南

## 📋 部署前准备

### 1. 获取 Gemini API Key
访问 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取您的 API Key。

### 2. 准备项目文件
确保您的项目包含以下文件：
- `app/main.py` - 主应用入口（FastAPI 应用）
- `Dockerfile` - Docker 配置
- `requirements.txt` - Python 依赖
- `configuration.json` - 魔搭配置文件（已包含）
- `static/` - 静态资源目录
- `templates/` - HTML 模板目录

## 🚀 部署步骤

### 方式一：通过魔搭创空间 Web 界面部署

1. **创建应用**
   - 访问 [魔搭创空间](https://www.modelscope.cn/studios)
   - 点击"创建应用空间"
   - 选择"自定义应用"

2. **上传代码**
   - 将整个项目文件夹打包成 zip
   - 或者通过 Git 仓库导入

3. **配置环境变量**
   在应用设置中添加以下环境变量：
   ```
   API_KEY=你的API_Key（Gemini 或 OpenAI 兼容）
   BASE_URL=（可选，Gemini 不需要，OpenAI 兼容 API 需要）
   MODEL=gemini-2.0-flash-exp（或你使用的模型名称）
   TAILIY_API_URL=（可选，网络搜索 API 地址）
   TAILIY_API_KEY=（可选，网络搜索 API Key）
   ```
   
   **注意**：
   - 如果使用 Gemini API，`API_KEY` 通常不以 `sk-` 开头，且不需要设置 `BASE_URL`
   - 如果使用 OpenAI 兼容 API（如 DeepSeek、OpenRouter 等），`API_KEY` 通常以 `sk-` 开头，需要设置 `BASE_URL`

4. **启动应用**
   - 点击"构建并启动"
   - 等待 Docker 镜像构建完成
   - 应用将在 7860 端口启动

### 方式二：通过 Git 仓库部署

1. **推送代码到 Git 仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <你的仓库地址>
   git push -u origin master
   ```

2. **在魔搭创空间导入**
   - 选择"从 Git 导入"
   - 输入仓库地址
   - 配置环境变量（同上）

## 📝 配置说明

### configuration.json
此文件告诉魔搭如何运行您的应用：
```json
{
  "framework": "fastapi",
  "language": "python",
  "type": "application",
  "runtime": "docker",
  "docker": {
    "dockerfile": "Dockerfile",
    "port": 7860
  }
}
```

### Dockerfile
确保使用正确的端口（7860）和启动命令：
```dockerfile
EXPOSE 7860
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

**重要**：启动命令必须使用 `app.main:app`，因为应用入口在 `app/main.py` 中。

## ⚙️ 环境变量说明

| 变量名 | 说明 | 默认值 | 是否必填 |
|--------|------|--------|---------|
| API_KEY | API 密钥（Gemini 或 OpenAI 兼容） | - | ✅ 必填 |
| BASE_URL | API 基础 URL（OpenAI 兼容 API 需要） | - | ❌ 可选 |
| MODEL | 使用的模型名称 | gemini-2.0-flash-exp | ❌ 可选 |
| TAILIY_API_URL | Taily 网络搜索 API 地址 | - | ❌ 可选 |
| TAILIY_API_KEY | Taily 网络搜索 API Key | - | ❌ 可选 |

**说明**：
- `API_KEY`：支持 Gemini API 和 OpenAI 兼容 API（如 DeepSeek、OpenRouter 等）
- `BASE_URL`：仅在使用 OpenAI 兼容 API 时需要设置
- `MODEL`：根据使用的 API 类型选择对应的模型名称

## 🔧 常见问题

### 1. 应用启动失败
- 检查环境变量是否正确配置
- 查看构建日志，确认依赖是否安装成功
- 确认 Dockerfile 中的端口是 7860

### 2. API 调用失败
- 验证 API_KEY 是否有效且未过期
- 检查 BASE_URL 是否正确（仅 OpenAI 兼容 API 需要）
- 确认模型名称与 API 提供商匹配
- 确认网络连接正常
- 查看应用日志了解详细错误信息

### 3. 静态资源加载失败
- 确保 `static/` 和 `templates/` 目录包含在部署包中
- 检查 `app/main.py` 中的静态文件挂载配置
- 确认 Dockerfile 中已正确复制这些目录

### 4. 应用启动失败（端口或模块错误）
- 确认 Dockerfile 中的启动命令是 `app.main:app` 而不是 `app:app`
- 检查端口是否为 7860
- 查看构建日志确认所有依赖已正确安装

### 5. 环境变量未生效
- 确认在魔搭创空间的环境变量设置中已正确配置
- 检查变量名是否拼写正确（区分大小写）
- 重启应用使环境变量生效

## 📊 性能优化建议

1. **使用流式响应**
   - 已在 `app/services.py` 中实现流式生成
   - 提供更好的用户体验，实时显示生成进度

2. **设置合理的超时时间**
   - 网页生成可能需要较长时间（30秒-5分钟）
   - 魔搭创空间默认超时时间通常足够

3. **添加请求限流**
   - 防止 API 配额耗尽
   - 可使用 slowapi 等库（可选）

4. **优化 Docker 镜像大小**
   - 使用 `python:3.10-slim` 基础镜像
   - 清理 pip 缓存（已在 Dockerfile 中配置）

## 🔒 安全建议

1. **保护 API Key**
   - 不要在代码中硬编码
   - 使用环境变量管理
   - 定期轮换密钥

2. **添加访问控制**
   - 考虑添加用户认证
   - 限制请求频率
   - 记录访问日志

## 📚 相关链接

- [魔搭创空间文档](https://www.modelscope.cn/docs/ModelScope%20Spaces)
- [Gemini API 文档](https://ai.google.dev/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

## 🆘 获取帮助

如果遇到问题：
1. 查看应用日志
2. 检查环境变量配置
3. 参考本文档的常见问题部分
4. 在魔搭社区提问

---

## 📦 项目结构说明

部署时确保以下目录和文件存在：

```
Baize/
├── app/                    # 应用主目录
│   ├── main.py            # FastAPI 应用入口
│   ├── config.py          # 配置管理
│   ├── routers.py         # 路由定义
│   ├── services.py        # 业务逻辑
│   ├── agents.py          # AI 代理
│   └── ...                # 其他模块
├── static/                 # 静态资源（CSS、JS、图片）
├── templates/             # HTML 模板
├── Dockerfile             # Docker 配置
├── requirements.txt       # Python 依赖
└── configuration.json     # 魔搭配置文件
```

**注意**：
- 首次部署可能需要 5-10 分钟来构建 Docker 镜像，请耐心等待
- 确保所有必要的文件都已提交到 Git 仓库或包含在 zip 包中
- 不要提交 `credentials.json` 文件（使用环境变量代替）

