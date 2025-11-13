"""Service layer for orchestrating agents and workflows."""
import json
import re
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import HTTPException

from .logging_config import get_logger
from .schemas import AgentState, ScienceEducationRequest
from .agents import SciencePlannerAgent, SciencePageGenerator
from .tools import TailiySearchTool


logger = get_logger(__name__)


class ScienceEducationService:
    """Service for executing the science education generation workflow."""

    @staticmethod
    async def _run_planner(
        state: AgentState,
        search_results: Optional[List[dict]] = None,
    ) -> Dict[str, Any]:
        """Call planner agent and update state with latest blueprint."""
        planner_raw = await SciencePlannerAgent.plan(
            topic=state.topic or "",
            search_results=search_results,
            history=state.messages,
            model=state.model,
        )

        def _sanitize_loose_quotes(text: str) -> str:
            """Escape un-delimited quotes within JSON string values."""
            chars: List[str] = []
            in_string = False
            i = 0
            length = len(text)

            while i < length:
                ch = text[i]
                if in_string:
                    if ch == "\\":
                        # Preserve escape sequences
                        chars.append(ch)
                        i += 1
                        if i < length:
                            chars.append(text[i])
                    elif ch == '"':
                        # Look ahead to determine if this quote ends the string value
                        j = i + 1
                        while j < length and text[j] in " \t\r\n":
                            j += 1
                        if j >= length or text[j] in ",}]":
                            chars.append('"')
                            in_string = False
                        else:
                            chars.extend(["\\", '"'])
                    else:
                        chars.append(ch)
                else:
                    chars.append(ch)
                    if ch == '"':
                        in_string = True
                i += 1

            return "".join(chars)

        def _parse_planner_output(raw: str) -> Dict[str, Any]:
            if raw is None or not str(raw).strip():
                raise ValueError("策划代理返回空响应")

            raw_str = str(raw).strip()

            def _strip_code_fence(text: str) -> str:
                if text.startswith("```"):
                    # Remove leading/trailing code fences if present
                    stripped = re.sub(r"^```(?:json)?\s*", "", text)
                    stripped = re.sub(r"\s*```$", "", stripped)
                    return stripped.strip()
                return text

            raw_candidate = _strip_code_fence(raw_str)

            try:
                return json.loads(raw_candidate)
            except json.JSONDecodeError:
                sanitized = _sanitize_loose_quotes(raw_candidate)
                if sanitized != raw_candidate:
                    try:
                        return json.loads(sanitized)
                    except json.JSONDecodeError:
                        pass

                match = re.search(r"\{[\s\S]*\}$", raw_candidate)
                if match:
                    try:
                        candidate = match.group(0)
                        try:
                            return json.loads(candidate)
                        except json.JSONDecodeError:
                            sanitized_inner = _sanitize_loose_quotes(candidate)
                            if sanitized_inner != candidate:
                                return json.loads(sanitized_inner)
                    except json.JSONDecodeError:
                        pass

                logger.error("策划代理返回的内容无法解析为 JSON: %s", raw_str)
                raise ValueError("策划代理返回内容无法解析为 JSON")

        planner_parsed = _parse_planner_output(planner_raw)

        state.need_search = bool(planner_parsed.get("need_search"))
        state.search_queries = [
            q.strip()
            for q in planner_parsed.get("search_queries", [])
            if isinstance(q, str) and q.strip()
        ]
        state.prompt_blueprint = planner_parsed
        state.planner_output_raw = planner_raw
        state.step = "planner_complete"

        return {
            "raw": planner_raw,
            "parsed": planner_parsed,
        }

    @staticmethod
    async def stream_science_page(
        request: ScienceEducationRequest,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream planner/search/generation events."""
        if not request.topic or not request.topic.strip():
            yield {"event": "error", "message": "主题不能为空"}
            return

        state = AgentState(
            topic=request.topic.strip(),
            messages=request.history or [],
            model=request.model,
        )

        try:
            planner_result = await ScienceEducationService._run_planner(state)
        except Exception as exc:
            logger.exception("策划代理执行失败: %s", exc)
            yield {"event": "error", "message": f"策划代理执行失败: {exc}"}
            return

        yield {
            "event": "planner",
            "step": "initial",
            "parsed": planner_result["parsed"],
            "raw": planner_result["raw"],
        }

        accumulated_search_results: List[dict] = []
        final_planner = planner_result["parsed"]

        if state.need_search and state.search_queries:
            for query in state.search_queries[:3]:
                state.search_attempts += 1
                result = await TailiySearchTool.search(query)
                accumulated_search_results.append(result)
                yield {
                    "event": "search",
                    "query": query,
                    "result": result,
                }

            state.search_results = accumulated_search_results

            try:
                planner_result = await ScienceEducationService._run_planner(
                    state,
                    search_results=accumulated_search_results,
                )
            except Exception as exc:
                logger.exception("带检索的策划执行失败: %s", exc)
                yield {"event": "error", "message": f"策划代理执行失败: {exc}"}
                return

            final_planner = planner_result["parsed"]
            final_planner["need_search"] = False

            yield {
                "event": "planner",
                "step": "refined",
                "parsed": final_planner,
                "raw": planner_result["raw"],
            }

        accumulated_html_parts: List[str] = []
        try:
            async for gen_event in SciencePageGenerator.stream_generate(
                topic=state.topic or "",
                planner_payload=final_planner,
                search_results=accumulated_search_results,
                history=state.messages,
                model=state.model,
            ):
                event_type = gen_event.get("type")
                content = gen_event.get("content") if isinstance(gen_event, dict) else None

                if event_type == "delta" and content:
                    accumulated_html_parts.append(content)
                    yield {
                        "event": "generation",
                        "delta": content,
                    }
                elif event_type == "final":
                    html = content or "".join(accumulated_html_parts)
                    state.generated_html = html
                    yield {
                        "event": "generation",
                        "html": html,
                        "planner_output": final_planner,
                        "planner_output_raw": state.planner_output_raw,
                        "search_results": accumulated_search_results,
                        "final": True,
                    }
        except Exception as exc:
            logger.exception("网页生成失败: %s", exc)
            yield {"event": "error", "message": f"网页生成失败: {exc}"}
            return

        yield {"event": "done"}

    @staticmethod
    async def generate_science_page(
        request: ScienceEducationRequest,
    ) -> Dict[str, Any]:
        """Fallback helper to execute full workflow and return aggregated result."""
        final_payload: Optional[Dict[str, Any]] = None
        error_message: Optional[str] = None

        async for event in ScienceEducationService.stream_science_page(request):
            if event.get("event") == "generation" and event.get("final"):
                final_payload = event
            elif event.get("event") == "error":
                error_message = event.get("message")

        if error_message:
            raise HTTPException(status_code=500, detail=error_message)

        if not final_payload or not final_payload.get("html"):
            raise HTTPException(status_code=500, detail="网页生成失败，未生成 HTML 内容")

        return {
            "topic": request.topic,
            "planner_output": final_payload.get("planner_output"),
            "planner_output_raw": final_payload.get("planner_output_raw"),
            "search_results": final_payload.get("search_results"),
            "html": final_payload.get("html"),
        }

