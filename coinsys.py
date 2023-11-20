from base import *
from logger import log
from time import time, ctime
from datetime import datetime

DATAPATH = "./user_data.json" # 储存玩家数据的json
SECONDS_IN_DAY = 86400 # 一天中的秒数

class User(object): # 未实现
    def __init__(self, uid: int):
        dat: dict = read_json(DATAPATH)
        user_dat: dict = dat[uid]

def _calExpToNextLevel(level: int) -> int:
    ''' 计算升到下一级所需的经验 
        原告：Mojang
    '''

    if 0 < level <= 15:
        return 2*level+7
    elif 15 < level <= 30:
        return 5*level-38
    else:
        return 9*level-158

def _update(user_data: dict) -> "tuple[dict, int]":
    ''' 更新玩家数据，应在每次exp有所变动时调用 '''
    isLevelUp = 0
    if user_data['exp'] >= (user_expToNextLevel := _calExpToNextLevel(user_data['level'])):
        user_data['exp'] -= user_expToNextLevel
        user_data['level'] += 1
        isLevelUp = user_data['level']
    return (user_data, isLevelUp)
    
def dailyExp(uid: int) -> int:
    ''' 每日在频道内发言可以获取的exp '''

    uid: str = str(uid)
    dat: dict = read_json(DATAPATH)
    if not uid in dat.keys() or dat[uid]['isSpoke'] == datetime.now().day: return 0
    # 玩家未注册或今天已发过言则直接返回0
    
    dat[uid]['exp'] += 3
    dat[uid]['isSpoke'] = datetime.now().day
    dat[uid], isLevelUp = _update(dat[uid]) # 更新玩家数据
    write_json(DATAPATH, dat)
    return isLevelUp

def register(uid: int) -> bool:
    ''' 新玩家注册 注册成功返回True，否则返回False '''
    uid: str = str(uid)
    dat: dict = read_json(DATAPATH)
    if not uid in dat.keys(): # 确认是新玩家
        dat[uid] = {
            "signCombo": 0, # 连续签到天数
            "lastSignTimeStamp": -1, # 上次签到时间戳
            "score": 0,   # 分数
            "level": 1,   # 等级
            "exp": 0,     # 经验值
            "isSpoke": 0, # 今日已发言
            "bio": "The owner is lazy and has no profile yet >_<", # 简介
            "colour": 15565216 # 颜色
        }

        write_json(DATAPATH, dat)
        return True
    return False

def profile(uid: int) -> "tuple[bool, list|None]":
    ''' 返回玩家数据 
        (玩家存在？, [等级，分数，简介，距离下一级经验，embed颜色])
    '''
    uid: str = str(uid)
    dat: dict = read_json(DATAPATH)
    
    if not uid in dat.keys(): # 玩家不存在
        return (False, None)
    
    user: "dict[str,]" = dat[uid]
    return (True, [user['level'], user['score'], user['bio'], _calExpToNextLevel(user['level'])-user['exp'], user['colour']])

def change(uid: int, item: str, value) -> bool:
    ''' 修改玩家个人资料 '''

    dat: dict = read_json(DATAPATH)
    if not item in ['colour', 'bio']: # 修改的项目不存在
        return False
    
    if item == 'colour': assert len((params := value.split())) == 3, value # 确保输入为R G B格式
    dat[str(uid)][f"{'colour' if item == 'colour' else ''}{'bio' if item == 'bio' else ''}"] = (15565216 if value == 'default' else sum([x*m for x, m in zip(map(int, params), [65536, 256, 1])])) if item == 'colour' else value
    write_json(DATAPATH, dat)
    return True

def sign_in(uid: int) -> "tuple[int]":
    ''' 玩家每日签到 '''
    uid: str = str(uid)
    dat: dict = read_json(DATAPATH)
    if not uid in dat.keys(): return (0, -1, -1) # 玩家不存在
    
    signTimeDelta = time() - dat[uid]['lastSignTimeStamp']
    if signTimeDelta < SECONDS_IN_DAY: 
        return (-1, sec_to_time(round(SECONDS_IN_DAY-signTimeDelta)), -1)
    elif SECONDS_IN_DAY < signTimeDelta < 2*SECONDS_IN_DAY:
        dat[uid]['score'] += 3
        dat[uid]['signCombo'] += 1
    else:
        dat[uid]['score'] += 3
        dat[uid]['signCombo'] = 1
    dat[uid]['lastSignTimeStamp'] = time()
    
    dat[uid]['score'] += (extraScore := (signCombo := dat[uid]['signCombo'])//3)

    write_json(DATAPATH, dat)
    return (1, extraScore, signCombo)

