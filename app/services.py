"""Service layer for orchestrating agents and workflows."""
from typing import Dict, Any
from fastapi import HTTPException

from .logging_config import get_logger
from .schemas import AgentState, ScienceEducationRequest
from .graph import create_science_education_graph


logger = get_logger(__name__)


class ScienceEducationService:
    """Service for executing the science education generation workflow."""

    @staticmethod
    async def generate_science_page(
        request: ScienceEducationRequest,
    ) -> Dict[str, Any]:
        if not request.topic or not request.topic.strip():
            raise HTTPException(status_code=400, detail="主题不能为空")

        initial_state = AgentState(
            topic=request.topic.strip(),
            messages=request.history or [],
            model=request.model,
        )

        graph = create_science_education_graph()

        try:
            result_state = await graph.ainvoke(initial_state)
        except Exception as exc:
            logger.exception("执行科普工作流失败: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        if result_state.get("error"):
            logger.error(
                "工作流返回错误: step=%s error=%s state=%s",
                result_state.get("step"),
                result_state.get("error"),
                result_state,
            )
            raise HTTPException(status_code=500, detail=result_state["error"])

        html = result_state.get("generated_html")
        if not html:
            logger.error("工作流未生成 HTML: state=%s", result_state)
            raise HTTPException(status_code=500, detail="网页生成失败，未生成 HTML 内容")

        return {
            "topic": request.topic,
            "planner_output": result_state.get("prompt_blueprint"),
            "planner_output_raw": result_state.get("planner_output_raw"),
            "search_results": result_state.get("search_results"),
            "html": html,
        }

