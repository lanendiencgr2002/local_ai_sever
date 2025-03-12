from dataclasses import dataclass, field
import aiohttp
import json
import time
import asyncio
import sys
from typing import List, Optional, Dict, Any, ClassVar
from pathlib import Path
from 配置类 import 配置类
from threading import Lock

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

@dataclass
class AIClient:
    @classmethod
    async def async_plus_ask(cls,config:AIConfig,question: str, system_prompt: str = "You are a helpful assistant. Use Chinese to respond.") -> str:
        start_time = time.time()
        try:
            response = await cls.async_normal_ask(config,question,system_prompt)
            elapsed_time = time.time() - start_time
            return {
                "status": "success",
                "time": round(elapsed_time, 2),
                "message": response,
                "message_length": len(response) if response else 0
            }
        except Exception as e:
            print(f"测试接口出错: {str(e)}")
            return {
                "status": "error",
                "time": -1,
                "message": f"错误：{str(e)}",
                "message_length": 0
            }
    @classmethod
    async def async_normal_ask(cls,config:AIConfig,question: str, system_prompt: str = "You are a helpful assistant. Use Chinese to respond.") -> str:
        url,payload,headers = cls._construct_requestall(config,system_prompt,question)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"API请求失败: {await response.text()}")
                return await cls._process_stream_response(response)
    @classmethod
    async def _process_stream_response(cls,response) -> str:
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
    @classmethod
    def _construct_requestall(cls,config,system_prompt,question):
        url=config['url']
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            "stream": True,
            "model": config['model'],
            "temperature": 0.2,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "top_p": 1,
        }
        headers = {
            'accept': 'application/json, text/event-stream',
            'authorization': f'Bearer {config["key"]}',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        return url,payload,headers

if __name__ == "__main__":
    async def run_test():
        result = await AIClient.async_plus_ask(AIConfig(url='https://api.openai.com/v1/chat/completions',key='sk-proj-1234567890',model='gpt-3.5-turbo'),'你好')
        print(f"测试结果：{result}")

    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_test())
