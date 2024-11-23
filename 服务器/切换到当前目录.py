import os
import sys
# 尝试切换当前目录 如果不行就忽略
try:    
    os.chdir('问gpt/服务器')
    sys.path.append("python_study")
    print('切换到当前目录：',os.getcwd())
except Exception as e:
    print('没关系可忽略，切换当前目录失败：', e)

