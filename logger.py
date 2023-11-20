from time import ctime
from typing import Union

class LogInfo(object):
    def __init__(self):
        self.info = 0
        self.warn = 0
        self.error = 0
        self.recentErrorInfo: "Union[dict[str, str], None]" = None
        # 最近的错误信息
        # 格式：
        # {
        #   "timestamp": 错误发生的时间,
        #   "traceback": 跟踪栈
        # }

logInfo = LogInfo()  # 实例化一个logInfo计数器

def log(detail, level="Info", traceback: str=None):
    ''' 日志总方法入口 '''
    if level == "Info": 
        logInfo.info += 1
        prompt_color = "\033[32m"
    elif level == "Warn": 
        logInfo.warn += 1
        prompt_color = "\033[33m"
    elif level == "Error": 
        logInfo.error += 1
        logInfo.recentErrorInfo = {"timestamp": ctime(), "traceback": traceback}
        prompt_color = "\033[1;91m"
    elif level == "Fatal": 
        prompt_color = "\033[4m\033[31m"
    else: prompt_color = "\033[0m"

    print(f"\033[0m[{ctime()}] [\033[1m{prompt_color}{level}\033[0m] {detail}")

    