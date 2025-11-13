"""Science education planner and generator agents."""

import asyncio
import json
from typing import List, Optional

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
        
        return response.choices[0].message.content.strip()


class SciencePageGenerator:
    """Agent responsible for generating the final science education page HTML."""
    
    @staticmethod
    async def generate(
        topic: str,
        planner_payload: Optional[dict],
        search_results: Optional[List[dict]] = None,
        history: Optional[List[dict]] = None,
        model: Optional[str] = None,
    ) -> str:
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
        
        model = model or config.science_generation_model
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
            temperature=0.25,
            stream=False,
        )
        
        return response.choices[0].message.content.strip()

