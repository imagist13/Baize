"""
FastAPI routers for planning and generation endpoints.
"""
import json
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from .config import config
from .schemas import (
    ChatRequest,
    CodePlanningRequest,
    PlanningRequest,
    CombinedPlanningRequest,
)
from .agents import AnimationGenerationAgent
from .services import PlanningService


# Templates
templates = Jinja2Templates(directory="templates")

# Routers
planning_router = APIRouter(prefix="", tags=["planning"])
generation_router = APIRouter(prefix="", tags=["generation"])
ui_router = APIRouter(prefix="", tags=["ui"])


@planning_router.post("/code/plan")
async def plan_code(request: CodePlanningRequest):
    """生成复杂代码实现的规划蓝图。"""
    return await PlanningService.execute_code_planning(request)


@planning_router.post("/plan")
async def plan_page(request: PlanningRequest):
    """生成网页规划蓝图与响应式策略。"""
    return await PlanningService.execute_page_planning(request)


@planning_router.post("/plan/combined")
async def plan_code_and_page(request: CombinedPlanningRequest):
    """先生成复杂代码规划，再基于结果优化页面规划。"""
    return await PlanningService.execute_combined_planning(request)


@generation_router.post("/generate")
async def generate(chat_request: ChatRequest, request: Request):
    """
    Main endpoint: POST /generate
    Accepts a JSON body with "topic" and optional "history".
    Returns an SSE stream.
    """
    
    async def event_generator():
        try:
            async for chunk in AnimationGenerationAgent.generate_stream(
                chat_request.topic, 
                chat_request.history
            ):
                if await request.is_disconnected():
                    print("Client disconnected, stopping stream")
                    break
                yield chunk
        except Exception as e:
            print(f"Error in event_generator: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
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


@ui_router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """Render the main UI page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "time": datetime.now(config.shanghai_tz).strftime("%Y%m%d%H%M%S"),
        }
    )

