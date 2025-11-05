"""
Entry point for the new LangGraph-based application.
"""
import uvicorn
import webbrowser
import time
from threading import Timer


def open_frontend():
    """在默认浏览器中打开前端页面。"""
    time.sleep(2)
    url = "http://localhost:8000"
    print(f"--- 在默认浏览器中打开前端: {url} ---")
    webbrowser.open(url)


if __name__ == "__main__":
    print("🚀 启动 AI Animation Backend (LangGraph 版本)")
    print("=" * 60)
    
    # Start browser opener in background
    Timer(2, open_frontend).start()
    
    # Run server using the new app structure
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable reload for development
    )

