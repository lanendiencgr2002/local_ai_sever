import aiohttp
import json
import time
import asyncio
import sys
import os

class ai列表:
    def __init__(self):
        # 获取当前文件所在目录
        当前目录 = os.path.dirname(os.path.abspath(__file__))
        配置文件路径 = os.path.join(当前目录, 'ai_config.json')
        
        try:
            with open(配置文件路径, 'r', encoding='utf-8') as f:
                配置 = json.load(f)
                self.url和key = 配置['ai_list']
        except FileNotFoundError:
            print(f"错误：找不到配置文件 {配置文件路径}")
            self.url和key = []
        except json.JSONDecodeError:
            print(f"错误：配置文件 {配置文件路径} 格式不正确")
            self.url和key = []

async def 问gpt问题(url, key, model, 问题="我帅不？", 提示词="You are a helpful assistant. Use Chinese to respond."):
    headers = {
        'accept': 'application/json, text/event-stream',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'authorization': f'Bearer {key}',
        'content-type': 'application/json',
        'origin': 'https://app.nextchat.dev',
        'priority': 'u=1, i',
        'referer': 'https://app.nextchat.dev/',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    # "max_tokens": 4096
    payload = {
        "messages": [
            {"role": "system", "content": 提示词},
            {"role": "user", "content": 问题},
        ],
        "stream": True,
        "model": model,
        "temperature": 0.2,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_p": 1,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            full_response = ""
            if response.status == 200:
                async for line in response.content:
                    if line:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = line[6:]
                            if data != '[DONE]':
                                try:
                                    json_data = json.loads(data)
                                    content = json_data['choices'][0]['delta'].get('content', '')
                                    full_response += content
                                except json.JSONDecodeError:
                                    print(f"无法解析JSON: {data}")
            else:
                print(f"请求失败，响应内容: {await response.text()},url:{url}")
                return None
            
            return full_response

async def 测试单个接口异步版(ai配置, 问题="你好"):
    开始 = time.time()
    try:
        回答 = await 问gpt问题(
            ai配置["url"],
            ai配置["key"],
            ai配置["model"],
            问题
        )
        用时 = time.time() - 开始
        return {
            "status": "success",
            "time": round(用时, 2),
            "message": 回答,
            "message_length": len(回答) if 回答 else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "time": -1,
            "message": None
        }

if __name__ == "__main__":
    ai = ai列表()
    测试配置 = ai.url和key[1]
    print('开始测试，测试配置为：',测试配置)

    async def 运行异步测试():
        结果 = await 测试单个接口异步版(测试配置, "你好")
        print(f"异步测试结果：{结果}")
    
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(运行异步测试())
