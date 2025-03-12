import requests
import concurrent.futures
import time
from typing import Dict, List

def 单次测试接口(url: str = "http://localhost:5000/chat", 问题: str = "你好") -> Dict:
    """执行单次接口测试，使用负载均衡（不指定具体接口）"""
    try:
        开始时间 = time.time()
        响应 = requests.post(url, json={
            "问题": 问题,
            # 不传入接口参数，使用服务器的负载均衡
        })
        用时 = time.time() - 开始时间
        
        if 响应.status_code == 200:
            响应数据 = 响应.json()
            return {
                "status": "success",
                "response_time": round(用时, 2),
                "response_data": 响应数据,
                "http_status": 响应.status_code
            }
        else:
            return {
                "status": "failed",
                "response_time": round(用时, 2),
                "error_message": 响应.text,
                "http_status": 响应.status_code
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "response_time": -1
        }

def 执行负载均衡测试(线程数: int = 3, 每个线程请求次数: int = 2) -> List[Dict]:
    """使用线程池执行多次负载均衡测试"""
    所有结果 = []
    总请求数 = 线程数 * 每个线程请求次数
    
    def 线程任务(任务序号: int):
        线程结果 = []
        for i in range(每个线程请求次数):
            结果 = 单次测试接口(问题=f"测试请求 #{任务序号}-{i}")
            线程结果.append({
                "thread_id": 任务序号,
                "request_id": i,
                "result": 结果
            })
        return 线程结果

    with concurrent.futures.ThreadPoolExecutor(max_workers=线程数) as executor:
        future_to_thread = {executor.submit(线程任务, i): i for i in range(线程数)}
        
        for future in concurrent.futures.as_completed(future_to_thread):
            thread_id = future_to_thread[future]
            try:
                结果 = future.result()
                所有结果.extend(结果)
            except Exception as e:
                所有结果.append({
                    "thread_id": thread_id,
                    "status": "error",
                    "error_message": str(e)
                })
    
    return 所有结果

if __name__ == "__main__":
    print("开始负载均衡测试...")
    开始时间 = time.time()
    
    测试结果 = 执行负载均衡测试(线程数=3, 每个线程请求次数=2)
    
    总用时 = time.time() - 开始时间
    print(f"\n测试完成，总用时: {round(总用时, 2)}秒")
    
    # 统计成功率
    成功次数 = sum(1 for 结果 in 测试结果 if 结果['result']['status'] == 'success')
    总次数 = len(测试结果)
    
    print(f"\n测试统计:")
    print(f"总请求数: {总次数}")
    print(f"成功请求数: {成功次数}")
    print(f"成功率: {(成功次数/总次数)*100:.2f}%")
    
    # 输出详细结果
    print("\n详细测试结果:")
    for 结果 in 测试结果:
        print(f"\n线程 #{结果['thread_id']}, 请求 #{结果['request_id']}:")
        print(f"状态: {结果['result']['status']}")
        print(f"响应时间: {结果['result']['response_time']}秒")
        if 结果['result']['status'] == 'success':
            print(f"响应数据: {结果['result']['response_data']}")
        else:
            print(f"错误信息: {结果['result'].get('error_message', '未知错误')}")