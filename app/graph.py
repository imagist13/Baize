"""
LangGraph workflow definitions for orchestrating the science education pipeline.
"""
import json
from typing import Any, Dict, List

from langgraph.graph import StateGraph, END

from .logging_config import get_logger
from .schemas import AgentState
from .agents import SciencePlannerAgent, SciencePageGenerator
from .tools import TailiySearchTool

logger = get_logger(__name__)


def create_science_education_graph():
    """
    Create a LangGraph workflow that mirrors the new product flow:

    月食主题 -> 提示词与网页 planer agent -> (可选) Tailiy 网络检索工具 -> 科普教育网页生成 -> 页面返回
    """

    async def planner_node(state: AgentState) -> Dict[str, Any]:
        """Decide whether to search and produce blueprint prompts."""
        logger.info("Planner node start: topic=%s existing_search=%s", state.topic, bool(state.search_results))
        try:
            planner_raw = await SciencePlannerAgent.plan(
                topic=state.topic or "",
                search_results=state.search_results,
                history=state.messages,
                model=state.model,
            )
        except Exception as exc:
            logger.exception("Planner agent failed: %s", exc)
            return {
                "error": f"策划代理执行失败: {exc}",
                "step": "planner_failed",
            }

        parsed: Dict[str, Any] = {}
        try:
            parsed = json.loads(planner_raw)
        except json.JSONDecodeError:
            logger.error("Planner output not JSON: %s", planner_raw)
            return {
                "error": "策划代理返回内容无法解析为 JSON",
                "planner_output_raw": planner_raw,
                "step": "planner_parse_failed",
            }

        need_search = bool(parsed.get("need_search", False))
        queries: List[str] = []
        for item in parsed.get("search_queries", []):
            if isinstance(item, str) and item.strip():
                queries.append(item.strip())

        planner_update = {
            "planner_output_raw": planner_raw,
            "prompt_blueprint": parsed,
            "knowledge_outline": parsed.get("knowledge_outline"),
            "need_search": need_search,
            "search_queries": queries,
            "step": "planner_complete",
            "metadata": {
                "json_prompt": parsed.get("json_prompt"),
                "safety_notes": parsed.get("page_blueprint", {}).get("safety_notes") if isinstance(parsed.get("page_blueprint"), dict) else None,
            },
        }

        if need_search and queries:
            planner_update["search_results"] = None  # reset stale results

        logger.info(
            "Planner node complete: need_search=%s queries=%s blueprint_keys=%s",
            need_search,
            queries,
            list(parsed.keys()),
        )
        return planner_update

    async def search_node(state: AgentState) -> Dict[str, Any]:
        """Invoke Tailiy search tool based on planner queries."""
        if not state.search_queries:
            return {
                "need_search": False,
                "search_results": [],
                "step": "search_skipped",
            }

        search_results = []
        for query in state.search_queries[:3]:
            result = await TailiySearchTool.search(query)
            search_results.append(result)

        logger.info(
            "Search node complete: queries=%s errors=%s",
            [r.get("query") for r in search_results],
            [r.get("error") for r in search_results if r.get("error")],
        )
        return {
            "search_results": search_results,
            "search_attempts": state.search_attempts + 1,
            "need_search": False,
            "step": "search_complete",
        }

    async def generation_node(state: AgentState) -> Dict[str, Any]:
        """Generate the final HTML page based on the planner blueprint."""
        planner_payload = state.prompt_blueprint or {}
        knowledge_outline = planner_payload.get("knowledge_outline") or state.knowledge_outline

        try:
            html = await SciencePageGenerator.generate(
                topic=state.topic or "",
                planner_payload=planner_payload,
                search_results=state.search_results,
                history=state.messages,
                model=state.model,
            )
        except Exception as exc:
            logger.exception("Generation node failed: %s", exc)
            return {
                "error": f"网页生成失败: {exc}",
                "step": "generation_failed",
            }

        logger.info("Generation node produced HTML length=%s", len(html or ""))
        return {
            "generated_html": html,
            "knowledge_outline": knowledge_outline,
            "step": "generation_complete",
        }

    def planner_router(state: AgentState) -> str:
        """Determine next step after planner node."""
        if state.error:
            return END
        if state.need_search:
            if state.search_results and all(not r.get("error") for r in state.search_results):
                logger.info("Planner router: using existing search results")
            else:
                if state.search_attempts >= 2:
                    logger.warning("Planner router: search skipped after %s attempts with errors", state.search_attempts)
                    state.need_search = False
                else:
                    logger.info("Planner router: retrying search (attempt %s)", state.search_attempts + 1)
                    return "search"
        if not state.prompt_blueprint:
            return END
        return "generation"

    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("search", search_node)
    workflow.add_node("generation", generation_node)

    workflow.set_entry_point("planner")
    workflow.add_conditional_edges(
        "planner",
        planner_router,
        {
            "search": "search",
            "generation": "generation",
            END: END,
        },
    )
    workflow.add_edge("search", "planner")
    workflow.add_edge("generation", END)

    return workflow.compile()
