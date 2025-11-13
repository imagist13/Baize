"""
Configuration module for API keys, model settings, and timezone.
"""
import json
import os
import pytz
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Application configuration."""
    
    def __init__(self):
        self.shanghai_tz = pytz.timezone("Asia/Shanghai")
        
        # 获取项目根目录（Baize/ 目录）
        # 从 app/config.py 向上两级到达项目根目录
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        
        # 加载环境变量
        load_dotenv(dotenv_path=project_root / ".env")
        
        # 从环境变量中获取配置
        self.api_key: str = os.environ.get("API_KEY", "") or ""
        self.base_url: str = os.environ.get("BASE_URL", "") or ""
        self.model: str = os.environ.get("MODEL", "") or ""
        self.tailiy_api_url: str = os.environ.get("TAILIY_API_URL", "") or ""
        self.tailiy_api_key: str = os.environ.get("TAILIY_API_KEY", "") or ""
        
        # 从credentials.json中获取配置（在项目根目录查找）
        credentials_path = project_root / "credentials.json"
        if credentials_path.exists():
            try:
                with open(credentials_path, encoding="utf-8") as f:
                    credentials = json.load(f)
                
                # 如果环境变量中没有配置，则从 credentials.json 读取
                if not self.api_key:
                    self.api_key = credentials.get("API_KEY", "") or ""
                if not self.base_url:
                    self.base_url = credentials.get("BASE_URL", "") or ""
                if not self.model:
                    self.model = credentials.get("MODEL", "") or ""
                if not self.tailiy_api_url:
                    self.tailiy_api_url = credentials.get("TAILIY_API_URL", "") or ""
                if not self.tailiy_api_key:
                    self.tailiy_api_key = credentials.get("TAILIY_API_KEY", "") or ""
                    
                print(f"✓ 从 {credentials_path} 加载配置")
            except Exception as e:
                print(f"⚠ 读取credentials.json文件失败: {e}")
        else:
            # 也在当前工作目录查找（向后兼容）
            if os.path.exists("credentials.json"):
                try:
                    with open("credentials.json", encoding="utf-8") as f:
                        credentials = json.load(f)
                    if not self.api_key:
                        self.api_key = credentials.get("API_KEY", "") or ""
                    if not self.base_url:
                        self.base_url = credentials.get("BASE_URL", "") or ""
                    if not self.model:
                        self.model = credentials.get("MODEL", "") or ""
                    if not self.tailiy_api_url:
                        self.tailiy_api_url = credentials.get("TAILIY_API_URL", "") or ""
                    if not self.tailiy_api_key:
                        self.tailiy_api_key = credentials.get("TAILIY_API_KEY", "") or ""
                    print(f"✓ 从当前目录的 credentials.json 加载配置")
                except Exception as e:
                    print(f"⚠ 读取credentials.json文件失败: {e}")
        
        # 设置默认模型（如果仍未设置）
        if not self.model:
            self.model = "gemini-2.0-flash-exp"
            print("⚠ 模型未设置，使用默认模型: gemini-2.0-flash-exp")
        
        # 检查配置完整性
        if not self.api_key:
            print("⚠ 警告: api_key未设置，请检查环境变量或credentials.json文件")
        else:
            print(f"✓ API Key 已配置: {self.api_key[:10]}...")
            
        if not self.base_url and self.api_key:
            # base_url 是可选的（Gemini 不需要，OpenAI 可以使用默认端点）
            # 只有非 Gemini 的 API key 才可能需要 base_url
            if self.api_key.startswith("sk-"):
                print("ℹ 提示: base_url未设置，将使用默认的OpenAI API端点")
        
        if not self.model:
            print("⚠ 警告: 模型未设置，请检查环境变量或credentials.json文件")
        else:
            print(f"✓ 模型已配置: {self.model}")
        
        # 为不同代理设置默认模型
        self.animation_model = "deepseek-ai/DeepSeek-V3.1-Terminus"
        self.code_planning_model = "Qwen/Qwen3-Coder-480B-A35B-Instruct"
        self.page_planning_model = "deepseek-ai/DeepSeek-V3.1-Terminus"
        self.science_planner_model = "deepseek-ai/DeepSeek-V3.1-Terminus"
        self.science_generation_model = "deepseek-ai/DeepSeek-V3.1-Terminus"
        
        if not self.tailiy_api_url:
            print("ℹ 提示: Taily 网络搜索 API 地址未配置，默认禁用网络搜索。")
        if not self.tailiy_api_key:
            print("ℹ 提示: Taily 网络搜索 API Key 未配置，默认禁用网络搜索。")
    
    def is_valid(self) -> bool:
        """Check if api_key and model are configured and valid.
        
        Note: base_url is optional. For Gemini API, base_url is not needed.
        For OpenAI-compatible APIs, base_url can be empty to use default endpoint.
        """
        # 检查必需字段是否设置（api_key 和 model）
        if not self.api_key or not self.model:
            return False
        
        # 检查api_key是否是占位符值（未配置）
        if self.api_key.startswith("sk-REPLACE_ME") or self.api_key == "YOUR_API_KEY_HERE":
            return False
        
        return True
    
    def is_gemini_key(self) -> bool:
        """Check if the API key is for Gemini.
        
        Gemini API keys typically don't start with 'sk-'.
        """
        if not self.api_key:
            return False
        return not self.api_key.startswith("sk-")


# Global config instance
config = Config()

