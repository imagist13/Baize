"""
Utility tools for planner agents, including Tailiy web search integration.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from .config import config


class TailiySearchTool:
    """Wrapper around Tailiy web search API used by planner agents."""

    DEFAULT_TIMEOUT = httpx.Timeout(15.0, connect=5.0)

    @classmethod
    async def search(
        cls,
        query: str,
        max_results: int = 5,
    ) -> Dict[str, Any]:
        """Perform a web search; returns normalized results."""
        if not query or not query.strip():
            return {"query": query, "error": "查询词为空", "results": []}

        if not config.tailiy_api_url or not config.tailiy_api_key:
            return {
                "query": query,
                "error": "Tailiy API 未配置",
                "results": [],
            }

        params = {"q": query.strip(), "k": max_results}
        headers = {
            "Authorization": f"Bearer {config.tailiy_api_key}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=cls.DEFAULT_TIMEOUT) as client:
            try:
                response = await client.get(
                    config.tailiy_api_url,
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                return {
                    "query": query,
                    "error": f"Tailiy API 响应异常: {exc.response.status_code}",
                    "results": [],
                }
            except httpx.RequestError as exc:
                return {
                    "query": query,
                    "error": f"Tailiy API 请求失败: {exc}",
                    "results": [],
                }

        try:
            payload = response.json()
        except ValueError as exc:
            return {"query": query, "error": f"解析响应失败: {exc}", "results": []}

        raw_results: List[Dict[str, Any]] = []
        if isinstance(payload, dict):
            raw_results = payload.get("data") or payload.get("results") or []
        elif isinstance(payload, list):
            raw_results = payload

        normalized: List[Dict[str, Any]] = []
        for item in raw_results:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "title": item.get("title") or item.get("name"),
                    "summary": item.get("summary") or item.get("snippet") or item.get("description") or "",
                    "highlights": item.get("highlights") or item.get("content") or [],
                    "source_url": item.get("url") or item.get("link"),
                    "raw": item,
                }
            )

        return {
            "query": query,
            "results": normalized,
            "raw": payload,
        }


