import asyncio
import json
import os
from datetime import datetime
from typing import AsyncGenerator, List, Optional

import pytz
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
try:
    import google.generativeai as genai
except ModuleNotFoundError:
    from google import genai
# -----------------------------------------------------------------------
# 0. 配置
# -----------------------------------------------------------------------
shanghai_tz = pytz.timezone("Asia/Shanghai")

# 优先从环境变量读取配置，如果没有则从 credentials.json 读取
API_KEY = os.environ.get("API_KEY", "")
BASE_URL = os.environ.get("BASE_URL", "")
MODEL = os.environ.get("MODEL", "")

# 如果环境变量中没有配置，尝试从 credentials.json 读取
if not API_KEY and os.path.exists("credentials.json"):
    credentials = json.load(open("credentials.json"))
    API_KEY = credentials["API_KEY"]
    BASE_URL = credentials.get("BASE_URL", "")
    MODEL = credentials.get("MODEL", "gemini-2.0-flash-exp")
elif not MODEL:
    MODEL = "gemini-2.0-flash-exp"

# 初始化客户端（仅当 API_KEY 有效时）
client = None
gemini_client = None
USE_GEMINI = False

if API_KEY and not API_KEY.startswith("sk-REPLACE_ME") and API_KEY != "YOUR_API_KEY_HERE":
    if API_KEY.startswith("sk-"):
        # 为 OpenRouter 添加应用标识
        extra_headers = {}
        if BASE_URL and "openrouter.ai" in BASE_URL.lower():
            extra_headers = {
                "HTTP-Referer": "https://github.com/fogsightai/fogsight",
                "X-Title": "Fogsight - AI Animation Generator"
            }
        
        client = AsyncOpenAI(
            api_key=API_KEY, 
            base_url=BASE_URL if BASE_URL else None,
            default_headers=extra_headers
        )
        USE_GEMINI = False
    else:
        if genai is None:
            print("警告: Google Generative AI SDK 未安装")
        else:
            os.environ["GEMINI_API_KEY"] = API_KEY
            gemini_client = genai.Client()
            USE_GEMINI = True
else:
    print("警告: 请在环境变量或 credentials.json 文件中配置 API_KEY")

templates = Jinja2Templates(directory="templates")

# -----------------------------------------------------------------------
# 1. FastAPI 初始化
# -----------------------------------------------------------------------
app = FastAPI(title="AI Animation Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    topic: str
    history: Optional[List[dict]] = None

# -----------------------------------------------------------------------
# 2. 核心：流式生成器 (现在会使用 history)
# -----------------------------------------------------------------------
async def llm_event_stream(
    topic: str,
    history: Optional[List[dict]] = None,
    model: str = None, # Will use MODEL from config if not specified
) -> AsyncGenerator[str, None]:
    # 检查是否配置了 API
    if not USE_GEMINI and client is None:
        yield f"data: {json.dumps({'error': '未配置 API，请在环境变量中设置 API_KEY'}, ensure_ascii=False)}\n\n"
        return
    
    if USE_GEMINI and gemini_client is None:
        yield f"data: {json.dumps({'error': 'Gemini 客户端未初始化'}, ensure_ascii=False)}\n\n"
        return
    
    history = history or []
    
    # Use configured model if not specified
    if model is None:
        model = MODEL
    
    # The system prompt is now more focused
    system_prompt = f"""你是一个专业的动画设计师和教育内容创作者。请为"{topic}"创建一个高质量的教育动画。

## 核心要求：
1. **动画质量**：创建流畅、专业的动画效果，使用 GSAP 或 CSS animations
2. **视觉设计**：
   - 采用现代、简洁的设计风格
   - 使用柔和的配色方案（如：#f0f4ff, #e3f2fd, #fce4ec 等浅色系）
   - 合理使用渐变、阴影、圆角等视觉元素
   - 确保视觉层次清晰，重点突出

3. **教育内容**：
   - 完整展示核心概念或过程
   - 配有清晰的中文解说文字
   - 文字位置合理，不遮挡关键内容
   - 使用图表、图示等辅助理解

4. **技术规范**：
   - 所有代码放在一个 HTML 文件中
   - 使用 HTML5 + CSS3 + JavaScript + SVG
   - 可使用 GSAP 库（从 CDN 加载）增强动画效果
   - 自动播放，无需用户交互
   - 响应式设计，适配不同屏幕尺寸
   - 容器尺寸：max-width: 1200px，居中显示

5. **动画要求**：
   - 总时长 15-30 秒
   - 流畅过渡，避免突兀变化
   - 使用 easing 函数让动画更自然
   - 可循环播放或在结束后暂停

## 示例结构：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <style>
        /* 现代化样式 */
    </style>
</head>
<body>
    <!-- 动画内容 -->
    <script>
        // GSAP 动画逻辑
    </script>
</body>
</html>
```

请直接生成完整的 HTML 代码，确保代码质量高、动画流畅、教育效果好。"""

    if USE_GEMINI:
        try:
            # 构建完整的prompt，包含历史对话
            if history:
                history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
                full_prompt = history_text + "\n\n" + system_prompt
                # 只在历史记录最后一条不是用户消息时才添加topic
                if not history or history[-1]['role'] != 'user':
                    full_prompt = full_prompt + "\n\nuser: " + topic
            else:
                full_prompt = system_prompt + "\n\nuser: " + topic
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: gemini_client.models.generate_content(
                    model=model, 
                    contents=full_prompt
                )
            )
            
            text = response.text
            chunk_size = 50
            
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i+chunk_size]
                payload = json.dumps({"token": chunk}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0.05)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            # 发送完成事件后再返回
            yield f'data: {json.dumps({"event": "[DONE]"})}\n\n'
            return
    else:
        # 构建消息列表 - 如果history为空或最后一条不是用户消息，则添加topic
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
        ]
        # 确保最后一条是用户消息
        if not history or history[-1]['role'] != 'user':
            messages.append({"role": "user", "content": topic})

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=0.8, 
            )
        except OpenAIError as e:
            print(f"OpenAI API error: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            # 发送完成事件后再返回
            yield f'data: {json.dumps({"event": "[DONE]"})}\n\n'
            return

        async for chunk in response:
            token = chunk.choices[0].delta.content or ""
            if token:
                payload = json.dumps({"token": token}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0.001)

    # 发送完成事件
    yield f'data: {json.dumps({"event": "[DONE]"})}\n\n'

# -----------------------------------------------------------------------
# 3. 路由 (CHANGED: Now a POST request)
# -----------------------------------------------------------------------
@app.post("/generate")
async def generate(
    chat_request: ChatRequest, # CHANGED: Use the Pydantic model
    request: Request,
):
    """
    Main endpoint: POST /generate
    Accepts a JSON body with "topic" and optional "history".
    Returns an SSE stream.
    """
    async def event_generator():
        try:
            async for chunk in llm_event_stream(chat_request.topic, chat_request.history):
                if await request.is_disconnected():
                    print("Client disconnected, stopping stream")
                    break
                yield chunk
        except Exception as e:
            print(f"Error in event_generator: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            # 即使出错也要发送完成事件
            yield f'data: {json.dumps({"event": "[DONE]"})}\n\n'


    async def wrapped_stream():
        async for chunk in event_generator():
            yield chunk

    headers = {
        "Cache-Control": "no-store",
        "Content-Type": "text/event-stream; charset=utf-8",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }
    return StreamingResponse(
        wrapped_stream(), 
        headers=headers,
        media_type="text/event-stream"
    )

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "time": datetime.now(shanghai_tz).strftime("%Y%m%d%H%M%S")})

# -----------------------------------------------------------------------
# 4. 本地启动命令
# -----------------------------------------------------------------------
# uvicorn app:app --reload --host 0.0.0.0 --port 8000


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)