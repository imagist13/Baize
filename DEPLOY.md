# 魔搭创空间部署指南

## 📋 部署前准备

### 1. 获取 Gemini API Key
访问 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取您的 API Key。

### 2. 准备项目文件
确保您的项目包含以下文件：
- `app.py` - 主应用文件
- `Dockerfile` - Docker 配置
- `requirements.txt` - Python 依赖
- `configuration.json` - 魔搭配置文件
- `static/` - 静态资源目录

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
   API_KEY=你的Gemini_API_Key
   BASE_URL=https://generativelanguage.googleapis.com/v1beta
   MODEL=gemini-2.0-flash-exp
   ```

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
确保使用正确的端口（7860）：
```dockerfile
EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

## ⚙️ 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| API_KEY | Gemini API 密钥 | 必填 |
| BASE_URL | Gemini API 基础 URL | https://generativelanguage.googleapis.com/v1beta |
| MODEL | 使用的模型名称 | gemini-2.0-flash-exp |

## 🔧 常见问题

### 1. 应用启动失败
- 检查环境变量是否正确配置
- 查看构建日志，确认依赖是否安装成功
- 确认 Dockerfile 中的端口是 7860

### 2. API 调用失败
- 验证 API_KEY 是否有效
- 检查 BASE_URL 是否正确
- 确认网络连接正常

### 3. 静态资源加载失败
- 确保 `static/` 目录包含在部署包中
- 检查 `app.py` 中的静态文件挂载配置

### 4. 视频生成失败
- 检查 prompt 是否符合 Gemini 要求
- 查看后端日志了解具体错误
- 验证模型是否支持视频生成

## 📊 性能优化建议

1. **使用流式响应**
   - 已在 `app.py` 中实现
   - 提供更好的用户体验

2. **设置合理的超时时间**
   - 视频生成可能需要较长时间
   - 建议设置 5-10 分钟超时

3. **添加请求限流**
   - 防止 API 配额耗尽
   - 可使用 slowapi 等库

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

**注意**：首次部署可能需要 5-10 分钟来构建 Docker 镜像，请耐心等待。

