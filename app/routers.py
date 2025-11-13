"""FastAPI routers for planning and generation endpoints."""
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
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
    """生成科普教育网页。"""
    return await ScienceEducationService.generate_science_page(request)


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

