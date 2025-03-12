from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
import asyncio
import time
import sys
from typing import List, Dict, Tuple
from 日志类 import LoggerManager
from itertools import cycle
from dataclasses import dataclass
from AIClass import AIClient
from 配置类 import 配置类
from pydantic import BaseModel
配置类.切换到脚本所在目录()
ai_configs = 配置类.读取toml文件('ai_configs.toml')

# 初始化日志系统
logger = LoggerManager(name="AI服务器自定义接口").get_logger()
# 创建 FastAPI 应用
app = FastAPI()

# 创建一个 AIClient 实例
ai_client = AIClient()

@dataclass
class LoadBalancer:
    current: cycle
    def __init__(self, api_configs: List[Dict]):
        global ai_configs
        self.current = cycle(list(enumerate(ai_configs['ai'])))
    def get_next_api(self) -> Tuple[int, Dict]:
        return next(self.current) 

负载均衡器 = LoadBalancer(ai_configs)

async def get_api_config():
    return 负载均衡器.get_next_api()

class ChatRequest(BaseModel):
    问题: str

@app.post("/chat")
async def chat(request: ChatRequest, api_config: tuple = Depends(get_api_config)):
    请求时间 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    接口标识, 选中的配置 = api_config
    try:
        结果 = await ai_client.async_plus_ask(选中的配置, request.问题)
        # 记录成功的请求和响应
        logger.info(
            f"请求时间: {请求时间}\n"
            f"接口ID: {接口标识}\n"
            f"请求内容: {request.问题}\n"
            f"响应内容: {结果}\n"
            f"状态: 成功\n"
            f"{'='*50}"
        )
        
        return {"data": 结果}
    
    except Exception as e:
        # 记录失败的请求和错误信息
        logger.error(
            f"请求时间: {请求时间}\n"
            f"请求内容: {request.问题}\n"
            f"错误信息: {str(e)}\n"
            f"状态: 失败\n"
            f"{'='*50}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test_all")
async def test_all(request: ChatRequest):
    global ai_client
    global ai_configs
    async def 测试单个(索引: int, 配置: dict) -> dict:
        结果 = await ai_client.async_plus_ask(配置, request.问题)
        return {
            "api_index": 索引,
            "api_url": 配置["url"],
            "api_model": 配置["model"],
            "test_result": 结果
        }
    
    任务列表 = [测试单个(i, 配置) for i, 配置 in enumerate(ai_configs['ai'])]
    开始时间 = time.time()
    结果 = await asyncio.gather(*任务列表)
    总用时 = time.time() - 开始时间

    return {
        "总用时": round(总用时, 2),
        "接口数量": len(ai_configs['ai']),
        "详细结果": sorted(结果, key=lambda x: x["test_result"]["time"])
    }

if __name__ == '__main__':
    import uvicorn
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    uvicorn.run(app, host="0.0.0.0", port=5000)