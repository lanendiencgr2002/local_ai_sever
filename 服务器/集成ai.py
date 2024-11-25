from dataclasses import dataclass
import aiohttp
import json
import time
import asyncio
import sys
from typing import List, Optional, Dict
from pathlib import Path

@dataclass
class AIConfig:
    url: str
    key: str
    model: str

@dataclass
class APIResponse:
    status: str
    time: float
    message: Optional[str] = None
    message_length: int = 0

class AIClient:
    def __init__(self, config: AIConfig):
        self.config = config
        self.headers = {
            'accept': 'application/json, text/event-stream',
            'authorization': f'Bearer {config.key}',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def ask(self, question: str, system_prompt: str = "You are a helpful assistant. Use Chinese to respond.") -> str:
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            "stream": True,
            "model": self.config.model,
            "temperature": 0.2,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "top_p": 1,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.config.url, headers=self.headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"API请求失败: {await response.text()}")
                
                return await self._process_stream_response(response)

    async def _process_stream_response(self, response) -> str:
        full_response = ""
        async for line in response.content:
            if line:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        continue
                    try:
                        json_data = json.loads(data)
                        content = json_data['choices'][0]['delta'].get('content', '')
                        full_response += content
                    except json.JSONDecodeError:
                        print(f"JSON解析错误: {data}")
        return full_response

class AIManager:
    # 单例模式：确保全局只有一个 AIManager 实例
    _instance = None

    def __new__(cls): # 会在类创建时调用
        # 如果实例不存在，则创建实例
        if cls._instance is None:
            # 调用父类的 __new__ 方法创建实例
            cls._instance = super().__new__(cls)
            
            # 加载 AI 配置
            cls._instance.configs = cls._instance._load_configs()
            
            # 将配置赋值给 url和key 属性，保持兼容性
            cls._instance.url和key = cls._instance.configs
        
        # 返回单例实例
        return cls._instance

    def __init__(self):
        # 由于使用单例模式，__init__ 方法不需要额外初始化
        pass

    def _load_configs(self) -> List[Dict]:
        """
        从 JSON 配置文件加载 AI 服务配置列表
        
        返回:
            List[Dict]: AI 服务配置列表，每个配置包含 URL、密钥等信息
        """
        # 获取配置文件路径（假设在同一目录下的 ai_config.json）
        config_path = Path(__file__).parent / 'ai_config.json'
        
        try:
            # 打开并读取 JSON 配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                # 返回 'ai_list' 键对应的配置列表
                return json.load(f)['ai_list']
        
        except FileNotFoundError:
            # 处理配置文件未找到的情况
            print(f"错误：找不到配置文件 {config_path}")
            return []
        
        except json.JSONDecodeError:
            # 处理 JSON 解析错误的情况
            print(f"错误：配置文件 {config_path} 格式不正确")
            return []

    async def test_endpoint(self, config: Dict, question: str = "你好") -> Dict:
        """
        测试单个 AI 服务接口的可用性和响应性能
        
        参数:
            config (Dict): AI 服务配置
            question (str, 可选): 测试问题，默认为 "你好"
        
        返回:
            Dict: 包含测试结果的字典，包括状态、响应时间、消息等
        """
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 使用配置创建 AI 客户端
            client = AIClient(AIConfig(**config))
            
            # 发送测试问题并等待响应
            response = await client.ask(question)
            
            # 计算响应耗时
            elapsed_time = time.time() - start_time
            
            # 返回成功的测试结果
            return {
                "status": "success",
                "time": round(elapsed_time, 2),  # 保留两位小数的响应时间
                "message": response,
                "message_length": len(response) if response else 0
            }
        
        except Exception as e:
            # 处理测试过程中可能出现的异常
            print(f"测试接口出错: {str(e)}")
            
            # 返回错误状态
            return {
                "status": "error",
                "time": -1,
                "message": f"错误：{str(e)}",
                "message_length": 0
            }

# 为了保持向后兼容性，用单例模式
ai列表 = AIManager
_manager = AIManager()
测试单个接口异步版 = _manager.test_endpoint

if __name__ == "__main__":
    async def run_test():
        manager = AIManager()  # 会返回同一个实例
        if manager.configs:
            result = await manager.test_endpoint(manager.configs[0])
            print(f"测试结果：{result}")

    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_test())
