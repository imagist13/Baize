# 白泽 - AI 知识动画生成器

## 项目简介

白泽是一款基于人工智能的知识动画生成器，能够根据用户提供的主题自动生成高质量、专业的教育动画。它结合了大语言模型的内容生成能力与现代前端技术，为用户提供直观、生动的知识表达方式。

## 核心功能

- **智能动画生成**：基于输入主题，自动生成包含动画效果的完整HTML页面
- **专业视觉设计**：采用现代、简洁的设计风格，包含柔和配色、渐变、阴影等元素
- **教育内容展示**：完整展示核心概念，配有清晰的中文解说文字
- **响应式设计**：适配不同屏幕尺寸，提供良好的观看体验
- **流畅动画效果**：使用GSAP库实现流畅、自然的动画过渡

## 技术栈

- **后端**：Python 3.10, FastAPI
- **前端**：HTML5, CSS3, JavaScript, SVG, GSAP
- **AI模型**：支持OpenAI API兼容接口或Google Gemini API
- **部署**：Docker容器化部署

## 快速开始

### 本地开发

1. **克隆项目**
```bash
# 克隆项目到本地
git clone https://github.com/your-username/baize.git
cd baize
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置API密钥**

创建`credentials.json`文件并填入您的API密钥：
```json
{
  "API_KEY": "your-api-key",
  "BASE_URL": "https://api.siliconflow.cn/v1",
  "MODEL": "deepseek-ai/DeepSeek-V3.1-Terminus"
}
```

或者通过环境变量配置：
```bash
# Windows
sets API_KEY=your-api-key
sets BASE_URL=https://api.siliconflow.cn/v1
sets MODEL=deepseek-ai/DeepSeek-V3.1-Terminus

# Linux/macOS
export API_KEY=your-api-key
export BASE_URL=https://api.siliconflow.cn/v1
export MODEL=deepseek-ai/DeepSeek-V3.1-Terminus
```

4. **启动应用**
```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

5. **访问应用**
打开浏览器，访问 http://localhost:8000

### Docker部署

1. **构建Docker镜像**
```bash
docker build -t baize-animator .
```

2. **运行Docker容器**
```bash
docker run -p 8000:7860 --env-file .env baize-animator
```

## 部署到ModelScope创空间

详细部署步骤请参考[MODELSCOPE_DEPLOY.md](MODELSCOPE_DEPLOY.md)文件。

### 主要步骤

1. 注册ModelScope账号
2. 准备API密钥
3. 创建新空间并配置环境变量
4. 上传项目文件或通过Git仓库导入
5. 启动部署并访问应用

## 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| API_KEY | AI模型API密钥 | 必填 |
| BASE_URL | API基础URL | 可选 |
| MODEL | 使用的模型名称 | gemini-2.0-flash-exp |

## 项目结构

```
baize/
├── app.py                 # 主应用文件
├── requirements.txt       # Python依赖
├── Dockerfile             # Docker构建文件
├── DEPLOY.md              # 部署文档
├── MODELSCOPE_DEPLOY.md   # ModelScope部署指南
├── templates/             # HTML模板
├── static/                # 静态资源
│   ├── favicon.png        # 网站图标
│   ├── logo.png           # 项目Logo
│   ├── script.js          # 前端脚本
│   └── style.css          # 样式文件
└── credentials.json       # 凭据配置（可选）
```

## API说明

### POST /generate

生成动画的主要接口。

**请求体**：
```json
{
  "topic": "要生成动画的主题",
  "history": [{"role": "user", "content": "历史对话内容"}]  // 可选
}
```

**响应**：
- 流式响应，包含生成的HTML代码

## 使用示例

1. 在应用界面输入您想要生成动画的主题，例如"太阳系行星运动"
2. 点击生成按钮
3. 系统将自动生成一个包含动画的HTML页面
4. 查看生成的动画效果，体验流畅的知识展示

## 常见问题

### API调用失败
- 检查API_KEY是否有效
- 确认BASE_URL配置正确
- 查看日志以获取详细错误信息

### 部署问题
- 确保Dockerfile中的端口配置为7860（ModelScope推荐端口）
- 检查环境变量是否正确配置
- 查看构建日志了解部署状态

## 贡献指南

欢迎提交Issue和Pull Request来改进本项目。在贡献代码前，请确保：

1. 遵循现有的代码风格
2. 为新功能添加适当的文档
3. 通过基本测试确保代码质量

## 许可证

[MIT License](LICENSE)

## 免责声明

本项目仅供学习和研究使用，生成的内容请确保符合相关法律法规，使用方需自行承担内容责任。
        
