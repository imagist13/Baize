"""FastAPI routers for planning and generation endpoints."""
import json
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from .config import config
from .schemas import ScienceEducationRequest
from .services import ScienceEducationService


# Templates
templates = Jinja2Templates(directory="templates")

# Routers
generation_router = APIRouter(prefix="", tags=["generation"])
ui_router = APIRouter(prefix="", tags=["ui"])


@generation_router.post("/generate")
async def generate_science_page(request: ScienceEducationRequest):
    """流式生成科普教育网页。"""

    async def event_stream():
        async for event in ScienceEducationService.stream_science_page(request):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        yield 'data: {"event": "[DONE]"}\n\n'

    headers = {
        "Cache-Control": "no-store",
        "Content-Type": "text/event-stream; charset=utf-8",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }

    return StreamingResponse(event_stream(), headers=headers, media_type="text/event-stream")


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

