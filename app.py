"""
白泽 - AI 知识动画生成器
兼容入口文件，用于 ModelScope 部署

此文件作为兼容层，导入新架构的 FastAPI 应用
"""
from app.main import app

# 导出 app 供 uvicorn 使用
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=7860,
        reload=False
    )

