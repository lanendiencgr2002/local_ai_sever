import json
from DrissionPage import ChromiumPage, ChromiumOptions
from concurrent.futures import ThreadPoolExecutor

def 初始化dp():
    co = ChromiumOptions().set_local_port(9222)
    page = ChromiumPage(addr_or_opts=co)
    page.timeout = 3
    return page
page=初始化dp()

api页面=[
    "api.yangtb2024.me",
    "api.aischat.xyz",
    "api.aigc369.com",
    "opus.gptuu.com",
    "api.cymru",
    "api.crond.dev",
    "m3.ckit.gold",
    "freeapi.aiiz.cc",
    "demo.voapi.top",
    "gala.chataiapi.com",
    "api.jimsblog.us.kg",
    "do.s1viv1s.win",
]

def 启动所有api页面():
    def 以获取token方式打开单个页面(页面):
        page.new_tab("https://" + 页面 + "/token")
    # 使用with语句管理线程池
    with ThreadPoolExecutor(max_workers=len(api页面)) as 线程池:
        for 页面 in api页面:
            线程池.submit(以获取token方式打开单个页面, 页面)
        # 等待所有任务完成
        线程池.shutdown(wait=True)

def 一键添加令牌获取key():
    def 添加令牌(tab):
        try:
            tab.ele('text=关闭公告',timeout=1).click()
            tab.ele('text=确认',timeout=1).click()
            tab.ele('text=确定',timeout=1).click()
        except:pass
        tab.ele('text:添加令牌').click()
        tab.ele('text:无限额度').click()
        tab.ele('text:提交').click()
    def 监听数据包(tab):
       tab.listen.start()
       tab.listen.wait(count=2,timeout=10)
    def 打印数据包(tab):
        for i in tab.listen.steps():
            # 过滤出非以/token结尾的请求
            if i.url.endswith('/token/'):continue
            try:
                with open('爬api.txt','a', encoding='utf-8') as f:
                    写的内容 = {
                        "url": tab.url.replace('/token', '/v1/chat/completions'),
                        "key": i.response.body['data'][0]['key'],
                        "model": ""
                    }
                    # 使用json.dumps()时设置indent参数来格式化JSON
                    格式化的json = json.dumps(写的内容, ensure_ascii=False, indent=4)
                    f.write(格式化的json + '\n')
                tab.listen.stop()
                print(f"{tab.url} 写入成功")
            except Exception as e:
                print(f"写入失败: {e}")

    # 过滤出所有可获取key的标签页对象
    所有标签页对象 = page.get_tabs()
    所有可获取key的标签页对象 = [i for i in 所有标签页对象 if i.url.endswith('/token')]
    
    # 添加检查逻辑
    if not 所有可获取key的标签页对象:
        print("没有找到可用的标签页，请先运行 启动所有api页面()")
        return

    # 监听数据包
    with ThreadPoolExecutor(max_workers=len(所有可获取key的标签页对象)) as 线程池:
        for 标签页对象 in 所有可获取key的标签页对象:
            线程池.submit(监听数据包, 标签页对象)
    
    # 一键添加令牌
    with ThreadPoolExecutor(max_workers=len(所有可获取key的标签页对象)) as 线程池:
        for 标签页对象 in 所有可获取key的标签页对象:
            线程池.submit(添加令牌, 标签页对象)
    
    # 打印数据包内容
    with ThreadPoolExecutor(max_workers=len(所有可获取key的标签页对象)) as 线程池:
        for 标签页对象 in 所有可获取key的标签页对象:
            线程池.submit(打印数据包, 标签页对象)



def 全都都删除直到删完():
    def 删除单个标签页(tab):
        tab.ele('text=删除').click()
        tab.ele('text=确定').click()
    def 查找删除按钮(tab):
        return tab.ele('text=删除')
    def 多线程查找(tabs):
        结果列表 = []
        with ThreadPoolExecutor(max_workers=len(tabs)) as 线程池:
            结果列表 = list(线程池.map(查找删除按钮, tabs))
        return any(结果列表)  # 只要有一个True就返回True

    # 过滤出所有可获取key的标签页对象
    所有标签页对象 = page.get_tabs()
    所有可获取key的标签页对象 = [i for i in 所有标签页对象 if i.url.endswith('/token')]

    # 查找是否能删不
    while 多线程查找(所有可获取key的标签页对象):
        # 多线程全部都删除
        with ThreadPoolExecutor(max_workers=len(所有可获取key的标签页对象)) as 线程池:
            for 标签页对象 in 所有可获取key的标签页对象:
                线程池.submit(删除单个标签页, 标签页对象)

if __name__ == '__main__':
    启动所有api页面()
    # 全都都删除直到删完()
    一键添加令牌获取key()
    print("结束")

