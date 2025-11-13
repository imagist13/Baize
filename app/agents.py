"""Science education planner and generator agents."""

import asyncio
import json
import re
from typing import AsyncGenerator, Dict, List, Optional, Tuple

from .config import config
from .clients import client_manager
from .prompts import (
    SCIENCE_PLANNER_PROMPT,
    SCIENCE_PAGE_GENERATION_PROMPT,
)


class SciencePlannerAgent:
    """Planner agent orchestrating search decisions and prompt blueprints."""
    
    @staticmethod
    async def plan(
        topic: str,
        search_results: Optional[List[dict]] = None,
        history: Optional[List[dict]] = None,
        model: Optional[str] = None,
    ) -> str:
        if not client_manager.is_ready():
            raise RuntimeError("未配置 API，请检查 API_KEY")
        
        model = model or config.science_planner_model
        history = history or []
        
        system_prompt = SCIENCE_PLANNER_PROMPT
        payload = {
            "topic": topic,
            "search_results": search_results or [],
        }
        user_prompt = json.dumps(payload, ensure_ascii=False, indent=2)
        
        if client_manager.use_gemini:
            if history:
                history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
                full_prompt = f"{history_text}\n\n系统: {system_prompt}\n\n用户: {user_prompt}"
            else:
                full_prompt = f"系统: {system_prompt}\n\n用户: {user_prompt}"
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client_manager.gemini_client.models.generate_content(
                    model=model,
                    contents=full_prompt
                )
            )
            
            return response.text.strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": user_prompt},
        ]
        
        response = await client_manager.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            stream=False,
        )
        
        content = response.choices[0].message.content
        if content is None or not content.strip():
            raise ValueError("策划代理返回空响应")
        
        return content.strip()


class SciencePageGenerator:
    """Agent responsible for generating the final science education page HTML."""
    
    @staticmethod
    def _prepare_generation_context(
        topic: str,
        planner_payload: Optional[dict],
        search_results: Optional[List[dict]],
        history: Optional[List[dict]],
        model: Optional[str],
    ) -> Tuple[str, str, str, List[dict], bool]:
        if not client_manager.is_ready():
            raise RuntimeError("未配置 API，请检查 API_KEY")
        
        planner_payload = planner_payload or {}
        if not isinstance(planner_payload, dict):
            raise ValueError("策划蓝图格式无效，必须为 JSON 对象")
        
        blueprint = planner_payload.get("page_blueprint")
        if not blueprint or not isinstance(blueprint, dict):
            raise ValueError("策划蓝图缺少 page_blueprint 字段，无法生成网页")
        
        json_prompt = planner_payload.get("json_prompt") if isinstance(planner_payload.get("json_prompt"), dict) else {}
        knowledge_outline = planner_payload.get("knowledge_outline")
        if knowledge_outline is None or not isinstance(knowledge_outline, list):
            knowledge_outline = []
        search_results = search_results or []
        
        model_name = model or config.science_generation_model
        history = history or []
        
        system_prompt = SCIENCE_PAGE_GENERATION_PROMPT
        payload = {
            "topic": topic,
            "blueprint": blueprint,
            "json_prompt": json_prompt,
            "knowledge_outline": knowledge_outline,
            "search_results": search_results,
        }
        user_prompt = json.dumps(payload, ensure_ascii=False, indent=2)
        
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": user_prompt},
        ]
        
        return model_name, system_prompt, user_prompt, messages, client_manager.use_gemini
    
    @staticmethod
    async def generate(
        topic: str,
        planner_payload: Optional[dict],
        search_results: Optional[List[dict]] = None,
        history: Optional[List[dict]] = None,
        model: Optional[str] = None,
    ) -> str:
        model_name, system_prompt, user_prompt, messages, use_gemini = SciencePageGenerator._prepare_generation_context(
            topic=topic,
            planner_payload=planner_payload,
            search_results=search_results,
            history=history,
            model=model,
        )
        
        if use_gemini:
            if history:
                history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
                full_prompt = f"{history_text}\n\n系统: {system_prompt}\n\n用户: {user_prompt}"
            else:
                full_prompt = f"系统: {system_prompt}\n\n用户: {user_prompt}"
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client_manager.gemini_client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
            )
            
            return _normalize_model_output(response.text)
        
        response = await client_manager.openai_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.25,
            stream=False,
        )
        
        return _normalize_model_output(response.choices[0].message.content)
    
    @staticmethod
    async def stream_generate(
        topic: str,
        planner_payload: Optional[dict],
        search_results: Optional[List[dict]] = None,
        history: Optional[List[dict]] = None,
        model: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Optional[str]], None]:
        model_name, system_prompt, user_prompt, messages, use_gemini = SciencePageGenerator._prepare_generation_context(
            topic=topic,
            planner_payload=planner_payload,
            search_results=search_results,
            history=history,
            model=model,
        )
        
        if use_gemini:
            if history:
                history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
                full_prompt = f"{history_text}\n\n系统: {system_prompt}\n\n用户: {user_prompt}"
            else:
                full_prompt = f"系统: {system_prompt}\n\n用户: {user_prompt}"
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client_manager.gemini_client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
            )
            yield {
                "type": "final",
                "content": _normalize_model_output(response.text),
            }
            return
        
        stream = await client_manager.openai_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.25,
            stream=True,
        )
        
        accumulated_chunks: List[str] = []
        async for chunk in stream:
            for choice in chunk.choices:
                delta = choice.delta.content if choice.delta else None
                if not delta:
                    continue
                accumulated_chunks.append(delta)
                yield {
                    "type": "delta",
                    "content": delta,
                }
        
        raw_text = "".join(accumulated_chunks)
        if raw_text:
            final_content = _normalize_model_output(raw_text)
        else:
            final_content = ""
        yield {
            "type": "final",
            "content": final_content,
        }


def _normalize_model_output(raw: Optional[str]) -> str:
    """Normalize model text output into clean HTML."""
    if raw is None:
        raise ValueError("网页生成代理返回空响应")

    text = raw.strip()
    if not text:
        raise ValueError("网页生成代理返回空响应")

    if text.startswith("```"):
        text = re.sub(r"^```(?:html|json|markdown)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

    match = re.search(r"<html[\s\S]*</html>", text, re.IGNORECASE)
    if match:
        return match.group(0).strip()

    return text

