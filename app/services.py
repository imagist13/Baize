"""
Service layer for orchestrating agents and workflows.
"""
import json
from typing import Optional, Dict, Any
from fastapi import HTTPException

from .schemas import (
    AgentState,
    CodePlanningRequest,
    PlanningRequest,
    CombinedPlanningRequest,
)
from .graph import (
    create_code_planning_graph,
    create_page_planning_graph,
    create_combined_planning_graph,
)


class PlanningService:
    """Service for executing planning workflows."""
    
    @staticmethod
    async def execute_code_planning(request: CodePlanningRequest) -> Dict[str, Any]:
        """Execute code planning workflow."""
        if not request.problem or not request.problem.strip():
            raise HTTPException(status_code=400, detail="问题描述不能为空")
        
        # Create initial state
        initial_state = AgentState(
            problem=request.problem,
            messages=request.history or [],
            model=request.model,
        )
        
        # Create and execute graph
        graph = create_code_planning_graph()
        
        try:
            result_state = await graph.ainvoke(initial_state)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        
        if result_state.get("error"):
            raise HTTPException(status_code=500, detail=result_state["error"])
        
        code_plan = result_state.get("code_plan_result", {})
        return {
            "parsed": code_plan.get("parsed"),
            "raw": code_plan.get("raw"),
        }
    
    @staticmethod
    async def execute_page_planning(request: PlanningRequest) -> Dict[str, Any]:
        """Execute page planning workflow."""
        if not request.topic or not request.topic.strip():
            raise HTTPException(status_code=400, detail="主题不能为空")
        
        # Create initial state
        initial_state = AgentState(
            topic=request.topic,
            messages=request.history or [],
            model=request.model,
        )
        
        # Create and execute graph
        graph = create_page_planning_graph()
        
        try:
            result_state = await graph.ainvoke(initial_state)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        
        if result_state.get("error"):
            raise HTTPException(status_code=500, detail=result_state["error"])
        
        page_plan = result_state.get("page_plan_result", {})
        return {
            "parsed": page_plan.get("parsed"),
            "raw": page_plan.get("raw"),
        }
    
    @staticmethod
    async def execute_combined_planning(
        request: CombinedPlanningRequest
    ) -> Dict[str, Any]:
        """Execute combined code and page planning workflow."""
        code_request = request.code_plan
        page_request = request.page_plan
        
        if not code_request.problem or not code_request.problem.strip():
            raise HTTPException(status_code=400, detail="问题描述不能为空")
        
        if not page_request.topic or not page_request.topic.strip():
            raise HTTPException(status_code=400, detail="主题不能为空")
        
        # Create initial state
        initial_state = AgentState(
            problem=code_request.problem,
            topic=page_request.topic,
            messages=code_request.history or [],
            model=code_request.model,
        )
        
        # Create and execute graph
        graph = create_combined_planning_graph()
        
        try:
            result_state = await graph.ainvoke(initial_state)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        
        if result_state.get("error"):
            raise HTTPException(status_code=500, detail=result_state["error"])
        
        code_plan = result_state.get("code_plan_result", {})
        page_plan = result_state.get("page_plan_result", {})
        
        return {
            "code_plan": {
                "parsed": code_plan.get("parsed"),
                "raw": code_plan.get("raw"),
            },
            "page_plan": {
                "parsed": page_plan.get("parsed"),
                "raw": page_plan.get("raw"),
            },
        }

