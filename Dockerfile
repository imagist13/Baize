# 使用官方 Python 3.10 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

# 创建一个非 root 用户运行应用（可选，但推荐）
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口（ModelScope 使用 7860）
EXPOSE 7860

# 健康检查（魔搭创空间会自动处理健康检查）
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/', timeout=5)" || exit 1

# 启动命令（使用新的 LangGraph 应用结构）
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]