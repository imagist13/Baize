"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import planning_router, generation_router, ui_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="AI Animation Backend",
        version="2.0.0",
        description="LangGraph-powered animation generation with code and page planning",
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )
    
    # Static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Include routers
    app.include_router(planning_router)
    app.include_router(generation_router)
    app.include_router(ui_router)
    
    return app


# Create app instance
app = create_app()

