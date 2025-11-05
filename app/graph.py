"""
LangGraph workflow definitions for orchestrating planning agents.
"""
import json
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .schemas import AgentState
from .agents import CodePlanningAgent, PagePlanningAgent


def create_combined_planning_graph():
    """
    Create a LangGraph workflow for combined code and page planning.
    
    Workflow:
    1. code_planning_node: Generate code architecture plan
    2. should_share_code_plan: Decide if code plan should be shared with page planning
    3. page_planning_node: Generate page layout plan (with optional code plan context)
    4. END
    """
    
    async def code_planning_node(state: AgentState) -> Dict[str, Any]:
        """Node that executes code planning."""
        try:
            code_plan_raw = await CodePlanningAgent.plan(
                problem=state.problem,
                history=state.messages,
                model=state.model,
            )
            
            # Try to parse JSON
            code_plan_parsed = None
            try:
                code_plan_parsed = json.loads(code_plan_raw)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
            
            return {
                "code_plan_result": {
                    "parsed": code_plan_parsed,
                    "raw": code_plan_raw,
                },
                "step": "code_planning_complete",
            }
        except Exception as e:
            return {
                "error": f"Code planning failed: {str(e)}",
                "step": "code_planning_failed",
            }
    
    async def page_planning_node(state: AgentState) -> Dict[str, Any]:
        """Node that executes page planning."""
        try:
            # Build history including code plan if available
            page_history = list(state.messages or [])
            
            if state.code_plan_result:
                code_plan = state.code_plan_result
                if isinstance(code_plan.get("parsed"), (dict, list)):
                    code_context_str = json.dumps(
                        code_plan["parsed"], 
                        ensure_ascii=False, 
                        indent=2
                    )
                else:
                    code_context_str = code_plan.get("raw", "")
                
                page_history.append({
                    "role": "user",
                    "content": (
                        "以下是复杂代码规划的结果，请基于此优化网页信息架构与响应式策略：\n"
                        f"{code_context_str}"
                    ),
                })
            
            page_plan_raw = await PagePlanningAgent.plan(
                topic=state.topic,
                history=page_history if page_history else None,
                model=state.model,
            )
            
            # Try to parse JSON
            page_plan_parsed = None
            try:
                page_plan_parsed = json.loads(page_plan_raw)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
            
            return {
                "page_plan_result": {
                    "parsed": page_plan_parsed,
                    "raw": page_plan_raw,
                },
                "step": "page_planning_complete",
            }
        except Exception as e:
            return {
                "error": f"Page planning failed: {str(e)}",
                "step": "page_planning_failed",
            }
    
    def should_continue_to_page(state: AgentState) -> str:
        """Conditional edge: check if we should continue to page planning."""
        if state.error:
            return END
        return "page_planning"
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("code_planning", code_planning_node)
    workflow.add_node("page_planning", page_planning_node)
    
    # Define edges
    workflow.set_entry_point("code_planning")
    workflow.add_conditional_edges(
        "code_planning",
        should_continue_to_page,
        {
            "page_planning": "page_planning",
            END: END,
        }
    )
    workflow.add_edge("page_planning", END)
    
    return workflow.compile()


def create_code_planning_graph():
    """
    Create a simple graph for standalone code planning.
    """
    
    async def code_planning_node(state: AgentState) -> Dict[str, Any]:
        """Node that executes code planning."""
        try:
            code_plan_raw = await CodePlanningAgent.plan(
                problem=state.problem,
                history=state.messages,
                model=state.model,
            )
            
            code_plan_parsed = None
            try:
                code_plan_parsed = json.loads(code_plan_raw)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
            
            return {
                "code_plan_result": {
                    "parsed": code_plan_parsed,
                    "raw": code_plan_raw,
                },
                "step": "code_planning_complete",
            }
        except Exception as e:
            return {
                "error": f"Code planning failed: {str(e)}",
                "step": "code_planning_failed",
            }
    
    workflow = StateGraph(AgentState)
    workflow.add_node("code_planning", code_planning_node)
    workflow.set_entry_point("code_planning")
    workflow.add_edge("code_planning", END)
    
    return workflow.compile()


def create_page_planning_graph():
    """
    Create a simple graph for standalone page planning.
    """
    
    async def page_planning_node(state: AgentState) -> Dict[str, Any]:
        """Node that executes page planning."""
        try:
            page_plan_raw = await PagePlanningAgent.plan(
                topic=state.topic,
                history=state.messages,
                model=state.model,
            )
            
            page_plan_parsed = None
            try:
                page_plan_parsed = json.loads(page_plan_raw)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
            
            return {
                "page_plan_result": {
                    "parsed": page_plan_parsed,
                    "raw": page_plan_raw,
                },
                "step": "page_planning_complete",
            }
        except Exception as e:
            return {
                "error": f"Page planning failed: {str(e)}",
                "step": "page_planning_failed",
            }
    
    workflow = StateGraph(AgentState)
    workflow.add_node("page_planning", page_planning_node)
    workflow.set_entry_point("page_planning")
    workflow.add_edge("page_planning", END)
    
    return workflow.compile()

