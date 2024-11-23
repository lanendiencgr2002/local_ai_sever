from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from itertools import cycle
from 集成ai import ai列表, 测试单个接口异步版
import sys
import asyncio
import time
import logging
from datetime import datetime
import os
from pathlib import Path

# 创建日志目录
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "ai_chat.log"

try:
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8', mode='a'),  # 文件处理器
            logging.StreamHandler()  # 控制台处理器
        ]
    )
    logging.info("日志系统初始化成功")
except Exception as e:
    print(f"日志配置错误: {e}")
    print(f"尝试写入的日志文件路径: {log_file}")

# 创建 FastAPI 应用
app = FastAPI()

# 初始化AI列表
ai实例 = ai列表()

class LoadBalancer:
    def __init__(self, apis):
        self.apis = list(enumerate(apis))  # 将配置列表转换为(索引, 配置)对的列表
        self.current = cycle(self.apis)
    
    def get_next_api(self):
        return next(self.current)

# 创建负载均衡器实例
负载均衡器 = LoadBalancer(ai实例.url和key)

# 定义请求模型
class ChatRequest(BaseModel):
    问题: str
    接口: Optional[str] = None  # 现在默认为None，表示使用负载均衡

class TestRequest(BaseModel):
    问题: Optional[str] = '你好'



@app.post("/chat")
async def chat(request: ChatRequest):
    请求时间 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if request.接口:
            # 如果指定了具体接口
            接口索引 = int(request.接口)
            if 接口索引 >= len(ai实例.url和key):
                raise HTTPException(status_code=400, detail='无效的接口选择')
            选中的配置 = ai实例.url和key[接口索引]
            接口标识 = 接口索引
        else:
            # 使用负载均衡获取下一个接口
            接口标识, 选中的配置 = 负载均衡器.get_next_api()
        
        结果 = await 测试单个接口异步版(选中的配置, request.问题)
        
        # 记录成功的请求和响应
        logging.info(
            f"请求时间: {请求时间}\n"
            f"接口ID: {接口标识}\n"
            f"请求内容: {request.问题}\n"
            f"响应内容: {结果}\n"
            f"状态: 成功\n"
            f"{'='*50}"
        )
        
        return {
            "data": 结果
        }
    except Exception as e:
        # 记录失败的请求和错误信息
        logging.error(
            f"请求时间: {请求时间}\n"
            f"请求内容: {request.问题}\n"
            f"错误信息: {str(e)}\n"
            f"状态: 失败\n"
            f"{'='*50}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test_all")
async def test_all(request: TestRequest):
    async def 测试单个(索引, 配置):
        结果 = await 测试单个接口异步版(配置, request.问题)
        return {
            "api_index": 索引,
            "api_url": 配置["url"],
            "api_model": 配置["model"],
            "test_result": 结果
        }
    
    # 创建所有接口的测试任务
    任务列表 = [测试单个(i, 配置) for i, 配置 in enumerate(ai实例.url和key)]
    
    # 并行执行所有测试
    开始时间 = time.time()
    结果 = await asyncio.gather(*任务列表)
    总用时 = time.time() - 开始时间

    # 结果通过用时排序
    结果 = sorted(结果, key=lambda x: x["test_result"]["time"])

    return {
        "总用时": round(总用时, 2),
        "接口数量": len(ai实例.url和key),
        "详细结果": 结果
    }

if __name__ == '__main__':
    import uvicorn
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    uvicorn.run(app, host="0.0.0.0", port=5000)