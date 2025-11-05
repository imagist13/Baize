"""
Configuration module for API keys, model settings, and timezone.
"""
import json
import os
import pytz
from typing import Optional


class Config:
    """Application configuration."""
    
    def __init__(self):
        self.shanghai_tz = pytz.timezone("Asia/Shanghai")
        
        # Load from environment variables first
        self.api_key: str = os.environ.get("API_KEY", "")
        self.base_url: str = os.environ.get("BASE_URL", "")
        self.model: str = os.environ.get("MODEL", "")
        
        # Fallback to credentials.json
        if not self.api_key and os.path.exists("credentials.json"):
            credentials = json.load(open("credentials.json"))
            self.api_key = credentials.get("API_KEY", "")
            self.base_url = credentials.get("BASE_URL", "")
            self.model = credentials.get("MODEL", "gemini-2.0-flash-exp")
        elif not self.model:
            self.model = "gemini-2.0-flash-exp"
        
        # Model defaults for different agents
        self.animation_model = "deepseek-ai/DeepSeek-V3.1-Terminus"
        self.code_planning_model = "Qwen/Qwen3-Coder-480B-A35B-Instruct"
        self.page_planning_model = "deepseek-ai/DeepSeek-V3.1-Terminus"
    
    def is_valid(self) -> bool:
        """Check if API key is configured and valid."""
        return (
            self.api_key 
            and not self.api_key.startswith("sk-REPLACE_ME") 
            and self.api_key != "YOUR_API_KEY_HERE"
        )
    
    def is_gemini_key(self) -> bool:
        """Check if the API key is for Gemini."""
        return not self.api_key.startswith("sk-")


# Global config instance
config = Config()

