"""
Agent nodes and workflow for LangGraph-based planning and generation.
"""
import asyncio
import json
from typing import List, Optional, AsyncGenerator
from openai import OpenAIError

from .config import config
from .clients import client_manager
from .schemas import AgentState
from .prompts import (
    ANIMATION_GENERATION_PROMPT,
    CODE_PLANNING_PROMPT,
    PAGE_PLANNING_PROMPT,
)


def format_bullet_section(items: Optional[List[str]], label: str) -> Optional[str]:
    """Format a list of items as a bulleted section."""
    if not items:
        return None
    
    cleaned_items = [item.strip() for item in items if item and item.strip()]
    if not cleaned_items:
        return None
    
    return f"{label}：\n- " + "\n- ".join(cleaned_items)


class AnimationGenerationAgent:
    """Agent for generating interactive animation HTML."""
    
    @staticmethod
    async def generate_stream(
        topic: str,
        history: Optional[List[dict]] = None,
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Generate animation HTML as a streaming response."""
        if not client_manager.is_ready():
            yield f"data: {json.dumps({'error': '未配置 API，请检查 API_KEY'}, ensure_ascii=False)}\n\n"
            yield f'data: {json.dumps({"event": "[DONE]"})}\n\n'
            return
        
        history = history or []
        model = model or config.animation_model
        
        system_prompt = ANIMATION_GENERATION_PROMPT.format(topic=topic)
        
        if client_manager.use_gemini:
            try:
                # Build full prompt with history
                if history:
                    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
                    full_prompt = history_text + "\n\n" + system_prompt
                    if not history or history[-1]['role'] != 'user':
                        full_prompt = full_prompt + "\n\nuser: " + topic
                else:
                    full_prompt = system_prompt + "\n\nuser: " + topic
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: client_manager.gemini_client.models.generate_content(
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
                yield f'data: {json.dumps({"event": "[DONE]"})}\n\n'
                return
        else:
            # OpenAI client
            messages = [
                {"role": "system", "content": system_prompt},
                *history,
            ]
            if not history or history[-1]['role'] != 'user':
                messages.append({"role": "user", "content": topic})
            
            try:
                response = await client_manager.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                    temperature=0.8,
                )
            except OpenAIError as e:
                print(f"OpenAI API error: {e}")
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
                yield f'data: {json.dumps({"event": "[DONE]"})}\n\n'
                return
            
            async for chunk in response:
                token = chunk.choices[0].delta.content or ""
                if token:
                    payload = json.dumps({"token": token}, ensure_ascii=False)
                    yield f"data: {payload}\n\n"
                    await asyncio.sleep(0.001)
        
        # Send completion event
        yield f'data: {json.dumps({"event": "[DONE]"})}\n\n'


class CodePlanningAgent:
    """Agent for generating code architecture plans."""
    
    @staticmethod
    async def plan(
        problem: str,
        target_users: Optional[str] = None,
        success_metrics: Optional[List[str]] = None,
        functional_requirements: Optional[List[str]] = None,
        non_functional_requirements: Optional[List[str]] = None,
        architecture_preferences: Optional[List[str]] = None,
        technology_stack: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        integration_points: Optional[List[str]] = None,
        data_models: Optional[List[str]] = None,
        edge_cases: Optional[List[str]] = None,
        history: Optional[List[dict]] = None,
        model: Optional[str] = None,
    ) -> str:
        """Generate a code planning document."""
        if not client_manager.is_ready():
            raise RuntimeError("未配置 API，请检查 API_KEY")
        
        model = model or config.code_planning_model
        history = history or []
        
        system_prompt = CODE_PLANNING_PROMPT
        
        user_sections = [
            f"核心问题：{problem.strip()}",
            f"目标用户：{target_users.strip()}" if target_users else None,
            format_bullet_section(success_metrics, "成功指标"),
            format_bullet_section(functional_requirements, "功能需求"),
            format_bullet_section(non_functional_requirements, "非功能需求"),
            format_bullet_section(architecture_preferences, "架构偏好"),
            format_bullet_section(technology_stack, "技术栈"),
            format_bullet_section(constraints, "限制条件"),
            format_bullet_section(integration_points, "对接接口"),
            format_bullet_section(data_models, "核心数据模型"),
            format_bullet_section(edge_cases, "已知边界情况"),
        ]
        
        user_prompt = "\n\n".join([section for section in user_sections if section])
        
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


class PagePlanningAgent:
    """Agent for generating page layout and responsive design plans."""
    
    @staticmethod
    async def plan(
        topic: str,
        audience: Optional[str] = None,
        goals: Optional[List[str]] = None,
        key_features: Optional[List[str]] = None,
        known_issues: Optional[List[str]] = None,
        style_preferences: Optional[List[str]] = None,
        primary_devices: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        history: Optional[List[dict]] = None,
        model: Optional[str] = None,
    ) -> str:
        """Generate a page planning document."""
        if not client_manager.is_ready():
            raise RuntimeError("未配置 API，请检查 API_KEY")
        
        model = model or config.page_planning_model
        history = history or []
        
        system_prompt = PAGE_PLANNING_PROMPT
        
        def join_lines(items: Optional[List[str]], label: str) -> str:
            if not items:
                return f"{label}：无特殊说明"
            return f"{label}：\n- " + "\n- ".join(s.strip() for s in items if s.strip())
        
        user_sections = [
            f"项目主题：{topic.strip()}",
            f"受众画像：{audience.strip()}" if audience else None,
            join_lines(goals, "业务/学习目标") if goals else None,
            join_lines(key_features, "关键功能或模块") if key_features else None,
            join_lines(known_issues, "当前痛点或适配问题") if known_issues else None,
            join_lines(style_preferences, "视觉风格偏好") if style_preferences else None,
            join_lines(primary_devices, "重点适配设备") if primary_devices else None,
            join_lines(constraints, "技术或资源限制") if constraints else None,
        ]
        
        user_prompt = "\n\n".join([section for section in user_sections if section])
        
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
            temperature=0.3,
            stream=False,
        )
        
        return response.choices[0].message.content.strip()

