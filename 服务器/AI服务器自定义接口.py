from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
import asyncio
import time
import sys

from models import ChatRequest, TestRequest
from load_balancer import LoadBalancer
from logger import setup_logger
from 集成ai import ai列表, 测试单个接口异步版

# 初始化日志系统
logger = setup_logger(maxBytes=2,backupCount=3)

# 创建 FastAPI 应用
app = FastAPI()

# 初始化AI列表和负载均衡器
ai实例 = ai列表()
负载均衡器 = LoadBalancer(ai实例.url和key)

async def get_api_config(request: ChatRequest):
    """获取API配置的依赖注入函数"""
    try:
        # 如果请求中指定了接口，则使用指定的接口 0/1/2/3
        if request.接口:
            接口索引 = int(request.接口)
            if 接口索引 >= len(ai实例.url和key):
                raise HTTPException(status_code=400, detail='无效的接口选择')
            return 接口索引, ai实例.url和key[接口索引]
        # 否则，使用负载均衡器选择一个接口
        return 负载均衡器.get_next_api()
    except ValueError:
        raise HTTPException(status_code=400, detail='接口参数格式错误')

@app.post("/chat")
async def chat(request: ChatRequest, api_config: tuple = Depends(get_api_config)):
    """处理聊天请求"""
    请求时间 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    接口标识, 选中的配置 = api_config
    
    try:
        结果 = await 测试单个接口异步版(选中的配置, request.问题)
        
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
async def test_all(request: TestRequest):
    """测试所有API接口"""
    async def 测试单个(索引: int, 配置: dict) -> dict:
        结果 = await 测试单个接口异步版(配置, request.问题)
        return {
            "api_index": 索引,
            "api_url": 配置["url"],
            "api_model": 配置["model"],
            "test_result": 结果
        }
    
    任务列表 = [测试单个(i, 配置) for i, 配置 in enumerate(ai实例.url和key)]
    开始时间 = time.time()
    结果 = await asyncio.gather(*任务列表)
    总用时 = time.time() - 开始时间

    return {
        "总用时": round(总用时, 2),
        "接口数量": len(ai实例.url和key),
        "详细结果": sorted(结果, key=lambda x: x["test_result"]["time"])
    }

if __name__ == '__main__':
    import uvicorn
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    uvicorn.run(app, host="0.0.0.0", port=5000)