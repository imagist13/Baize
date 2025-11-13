import json
import os
import pytz
from dotenv import load_dotenv
from pathlib import Path



class Config:
    def __init__(self):
        #设置时区
        self.shanghai_tz = pytz.timezone("Asia/Shanghai") #时区设置为东八区
        
        # 获取项目根目录（Baize/ 目录）
        # 从 app/config.py 向上两级到达项目根目录
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        
        # 加载环境变量
        load_dotenv(dotenv_path=project_root / ".env")
        #从环境变量中获取api_key,base_url,model
        #主要用于在创空间部署时，将环境变量设置到创空间中

        self.api_key : str = os.environ.get("API_KEY") or ""
        self.base_url : str = os.environ.get("BASE_URL") or ""
        self.model : str = os.environ.get("MODEL") or ""


        # 从credentials.json中获取配置（在项目根目录查找）
        credentials_path = project_root / "credentials.json"
        
        #从credentials.json中获取api_key,base_url,model
        #用于本地开发（如果环境变量中没有配置）
        if os.path.exists("credentials.json"):
            try:
                with open("credentials.json", encoding="utf-8") as f:
                    credentials = json.load(f)
                if not self.api_key:
                    self.api_key = credentials.get("API_KEY") or ""
                if not self.base_url:
                    self.base_url = credentials.get("BASE_URL") or ""
                if not self.model:
                    self.model = credentials.get("MODEL") or ""
            except Exception as e:
                print(f"读取credentials.json文件失败: {e}")
        
    #接下来要进行模型测试
    def is_valid(self) -> bool:
        """检查api_key,base_url,model是否设置"""
        # 检查是否为空
        if not self.api_key or not self.model:
            return False
        
        # 检查api_key是否是占位符值（未配置）
        if self.api_key.startswith("sk-REPLACE_ME") or self.api_key == "YOUR_API_KEY_HERE":
            return False
        
        return True

if __name__ == "__main__":
    config = Config()
    print(config.is_valid())

