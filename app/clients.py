"""
Client initialization for OpenAI and Gemini APIs.
"""
import os
from typing import Optional
from openai import AsyncOpenAI

try:
    import google.generativeai as genai
except ModuleNotFoundError:
    from google import genai

from .config import config


class ClientManager:
    """Manages API clients for OpenAI and Gemini."""
    
    def __init__(self):
        self.openai_client: Optional[AsyncOpenAI] = None
        self.gemini_client: Optional[genai.Client] = None
        self.use_gemini: bool = False
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize appropriate client based on API key."""
        if not config.is_valid():
            print("警告: 请在环境变量或 credentials.json 文件中配置 API_KEY")
            return
        
        if config.is_gemini_key():
            # Initialize Gemini client
            if genai is None:
                print("警告: Google Generative AI SDK 未安装")
                return
            
            os.environ["GEMINI_API_KEY"] = config.api_key
            self.gemini_client = genai.Client()
            self.use_gemini = True
            print("✓ Gemini 客户端初始化成功")
        else:
            # Initialize OpenAI client
            extra_headers = {}
            if config.base_url and "openrouter.ai" in config.base_url.lower():
                extra_headers = {
                    "HTTP-Referer": "https://github.com/fogsightai/fogsight",
                    "X-Title": "Fogsight - AI Animation Generator"
                }
            
            self.openai_client = AsyncOpenAI(
                api_key=config.api_key,
                base_url=config.base_url if config.base_url else None,
                default_headers=extra_headers
            )
            self.use_gemini = False
            print("✓ OpenAI 客户端初始化成功")
    
    def get_client(self):
        """Get the active client."""
        if self.use_gemini:
            return self.gemini_client
        return self.openai_client
    
    def is_ready(self) -> bool:
        """Check if a client is ready."""
        if self.use_gemini:
            return self.gemini_client is not None
        return self.openai_client is not None


# Global client manager
client_manager = ClientManager()

