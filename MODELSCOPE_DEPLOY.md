# ModelScope 创空间部署指南

本文档详细说明如何将白泽项目部署到 ModelScope 创空间。

## 📋 前置准备

1. **注册 ModelScope 账号**
   - 访问：https://modelscope.cn
   - 注册并登录账号

2. **准备 API 密钥**
   - 已配置好硅基流动 API
   - API_KEY: `sk-zvzsmiotxvpntxznmzuypiufkprfnyhwobunwczcafdchcum`
   - BASE_URL: `https://api.siliconflow.cn/v1`
   - MODEL: `deepseek-ai/DeepSeek-V3.1-Terminus`

## 🚀 部署步骤

### 方法一：通过 Web 界面部署（推荐）

#### 1. 创建新空间

1. 访问 ModelScope 创空间：https://modelscope.cn/studios
2. 点击右上角 **"创建空间"** 按钮
3. 填写空间信息：
   - **空间名称**：`baize-knowledge-animator`（或自定义）
   - **空间描述**：`白泽 - AI 知识动画生成器`
   - **可见性**：选择"公开"或"私有"
   - **运行时类型**：选择 **"Docker 应用"**
   - **基础镜像**：选择 `Python 3.10`
4. 点击 **"创建"**

#### 2. 上传项目文件

在创建的空间中，上传以下文件：

```
baize/
├── app.py                 # 主应用文件
├── requirements.txt       # Python 依赖
├── Dockerfile            # Docker 构建文件
├── configuration.json    # ModelScope 配置
├── .dockerignore        # Docker 忽略文件
└── README.md            # 项目说明
```

**上传方式**：
- 方式 1：直接在 Web 界面点击"上传文件"逐个上传
- 方式 2：使用 Git 仓库同步（见方法二）

#### 3. 配置环境变量（已在 configuration.json 中配置）

环境变量已经在 `configuration.json` 中预配置：

```json
{
  "environment": {
    "API_KEY": "sk-zvzsmiotxvpntxznmzuypiufkprfnyhwobunwczcafdchcum",
    "BASE_URL": "https://api.siliconflow.cn/v1",
    "MODEL": "deepseek-ai/DeepSeek-V3.1-Terminus"
  }
}
```

**注意**：如果需要修改，可以在空间设置中手动添加/修改环境变量。

#### 4. 启动部署

1. 文件上传完成后，点击 **"构建"** 按钮
2. 等待 Docker 镜像构建（首次构建约 5-10 分钟）
3. 构建成功后，系统会自动启动应用
4. 查看 **"日志"** 确认启动成功

#### 5. 访问应用

- 构建成功后，点击空间 URL 即可访问
- URL 格式：`https://modelscope.cn/studios/你的用户名/baize-knowledge-animator`

---

### 方法二：通过 Git 仓库部署

#### 1. 准备 Git 仓库

如果你的代码在 Git 仓库中（GitHub/GitLab/Gitee）：

```bash
# 1. 确保所有文件已提交
git add .
git commit -m "Ready for ModelScope deployment"
git push
```

#### 2. 连接仓库到 ModelScope

1. 在创建空间时选择 **"从 Git 导入"**
2. 输入你的 Git 仓库 URL
3. 选择分支（通常是 `main` 或 `master`）
4. ModelScope 会自动读取 `configuration.json` 配置
5. 点击 **"创建并部署"**

#### 3. 自动部署

- 每次推送代码到 Git 仓库，ModelScope 会自动重新构建
- 无需手动上传文件

---

## 🔍 验证部署

### 1. 检查日志

在空间管理界面查看日志，应该看到：

```
INFO:     Started server process [xxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)
```

### 2. 测试功能

1. 访问空间 URL
2. 在输入框输入测试问题，例如：
   - "讲解一下二叉树"
   - "解释什么是量子纠缠"
3. 查看 AI 是否正常响应
4. 测试"新对话"按钮是否工作

### 3. 常见问题排查

#### 问题 1：构建失败

**可能原因**：
- Dockerfile 语法错误
- requirements.txt 依赖安装失败

**解决方法**：
1. 查看构建日志
2. 检查 Dockerfile 和 requirements.txt
3. 确保所有文件格式正确（UTF-8 编码）

#### 问题 2：启动失败

**可能原因**：
- 环境变量未配置
- 端口配置错误

**解决方法**：
1. 检查 configuration.json 中的环境变量
2. 确认 Dockerfile 中的端口是 7860
3. 查看应用日志

#### 问题 3：API 调用失败

**可能原因**：
- API_KEY 无效或过期
- BASE_URL 无法访问
- 模型名称错误

**解决方法**：
1. 验证 API_KEY 是否有效
2. 测试 BASE_URL 是否可访问
3. 检查 MODEL 名称是否正确

---

## 📊 资源配置

ModelScope 创空间默认资源配置：

- **CPU**：2 核
- **内存**：8GB
- **存储**：20GB
- **GPU**：无（本项目不需要）

如需更多资源，可以在空间设置中申请升级。

---

## 🔒 安全建议

### 保护 API 密钥

虽然当前 API_KEY 已在 `configuration.json` 中，但建议：

1. **使用环境变量**（更安全）
   - 在 ModelScope 空间设置中添加环境变量
   - 从 configuration.json 中删除敏感信息

2. **设置空间为私有**
   - 避免 API_KEY 泄露
   - 只允许授权用户访问

3. **定期轮换密钥**
   - 定期更换 API_KEY
   - 监控 API 使用情况

### 修改为使用环境变量（可选）

如果希望更安全，修改 `configuration.json`：

```json
{
  "framework": "fastapi",
  "language": "python",
  "type": "application",
  "runtime": "docker",
  "docker": {
    "dockerfile": "Dockerfile",
    "port": 7860
  },
  "requirements": "requirements.txt"
}
```

然后在 ModelScope 空间设置中手动添加环境变量：
- `API_KEY`
- `BASE_URL`
- `MODEL`

---

## 🎯 部署后优化

### 1. 性能优化

- 监控 API 调用次数
- 优化响应时间
- 考虑添加缓存机制

### 2. 功能增强

- 添加用户认证
- 实现动画历史记录
- 支持更多动画类型

### 3. 监控和维护

- 定期查看日志
- 监控 API 使用量
- 更新依赖包

---

## 📞 获取帮助

- **ModelScope 文档**：https://modelscope.cn/docs
- **创空间指南**：https://modelscope.cn/docs/ModelScope%20Studios
- **问题反馈**：https://github.com/modelscope/modelscope/issues

---

## ✅ 部署检查清单

在部署前，请确认：

- [ ] 所有文件已准备好（app.py, requirements.txt, Dockerfile, configuration.json）
- [ ] API_KEY 有效且可用
- [ ] Dockerfile 端口配置为 7860
- [ ] configuration.json 格式正确
- [ ] requirements.txt 包含所有依赖
- [ ] 本地测试通过
- [ ] 已阅读安全建议

---

**祝部署顺利！** 🎉

如有问题，请查看 ModelScope 文档或联系技术支持。

