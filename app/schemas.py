"""
Pydantic schemas for request/response models.
"""
from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request model for chat/generation."""
    topic: str
    history: Optional[List[dict]] = None


class PlanningRequest(BaseModel):
    """Request model for page planning."""
    topic: str
    audience: Optional[str] = None
    goals: Optional[List[str]] = None
    key_features: Optional[List[str]] = None
    known_issues: Optional[List[str]] = None
    style_preferences: Optional[List[str]] = None
    primary_devices: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    history: Optional[List[dict]] = None
    model: Optional[str] = None


class CodePlanningRequest(BaseModel):
    """Request model for code planning."""
    problem: str
    target_users: Optional[str] = None
    success_metrics: Optional[List[str]] = None
    functional_requirements: Optional[List[str]] = None
    non_functional_requirements: Optional[List[str]] = None
    architecture_preferences: Optional[List[str]] = None
    technology_stack: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    integration_points: Optional[List[str]] = None
    data_models: Optional[List[str]] = None
    edge_cases: Optional[List[str]] = None
    history: Optional[List[dict]] = None
    model: Optional[str] = None


class CombinedPlanningRequest(BaseModel):
    """Request model for combined planning."""
    code_plan: CodePlanningRequest
    page_plan: PlanningRequest
    share_code_plan_with_page: bool = True


class AgentState(BaseModel):
    """State model for LangGraph agents."""
    class Config:
        arbitrary_types_allowed = True
    
    # Common fields
    messages: List[dict] = []
    error: Optional[str] = None
    
    # Planning fields
    topic: Optional[str] = None
    problem: Optional[str] = None
    code_plan_result: Optional[dict] = None
    page_plan_result: Optional[dict] = None
    
    # Generation fields
    generated_html: Optional[str] = None
    
    # Metadata
    model: Optional[str] = None
    step: Optional[str] = None

