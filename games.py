from random import randint, choice, shuffle
from requests import get
import bs4

def quiz() -> tuple:
    PLAN = ["+", "-", "*"]
    calculation = str(randint(0,100))
    for _ in range(randint(1,3)): calculation += choice(PLAN)+str(randint(0, 100))
    return (calculation.replace("*","×")+"=?", eval(calculation))

def analyzeQrcode(url: str):
    req = get("https://zxing.org/w/decode?u="+url)
    soup = bs4.BeautifulSoup(req.text, 'html.parser')
    try:
        link = soup.body.div.table.tr.find_all()[1].pre.contents[0]
        return link
    except AttributeError:
        return

class Roulette(object):
    """ 俄罗斯轮盘主类 """
    def __init__(self, prize=None, once=""):
        self.ammo = [1,0,0,0,0,0] # 共6个子弹槽，装填1发子弹
        self.player = [] # 进行过轮盘的玩家列表
        self.prize = prize # 轮盘击发奖励
        self.once = bool(once) # once模式，一人只能进行一次

    def shot(self, user_id):
        if user_id in self.player and self.once: return -1 # once模式下一人进行超过一次轮盘，返回-1 操作无效

        self.player.append(user_id) 
        selected = choice(self.ammo) # 随机选择列表中一个元素，返回
        if not selected: self.ammo.remove(0) # 未击发，去除一个空槽

        if len(self.ammo) <= 1: # 仅剩一轮，平局
            return None
        
        return selected # 返回 1 击发 0 未击发

class TChess(object):
    def __init__(self, users: list, group_id: int, gamb=0):
        self.plate = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.group_id = group_id
        self.round = choice(["O", "X"])
        shuffle(users)
        self.users = {"O": users[0], "X": users[1]}
    
    def isWin(self):
        """ 判断棋盘胜负结果 """
        for i in range(3): # 每行
            if self.plate[i][0] == self.plate[i][1] == self.plate[i][2] != None: return True
        
        for i in range(3): # 每列
            if self.plate[0][i] == self.plate[1][i] == self.plate[2][i] != None: return True
        
        if ( 
            (self.plate[0][0] == self.plate[1][1] == self.plate[2][2] != None) or # 右下对角
            (self.plate[0][2] == self.plate[1][1] == self.plate[2][0] != None)    # 左上对角
            ): return True
        
        for row in self.plate:
            for single in row:
                if single is None: return False # 胜负未定
        return None # 棋盘已满，平局
    
    def printPlate(self) -> str:
        text = ""
        for row in self.plate:
            for single in row: # ✖️⭕⬜
                if single == "X": text += "✖️"
                elif single == "O": text += "⭕"
                else: text += "⬜"
            text += "\n"

        return text

    def go(self, inp: list):
        if not self.plate[inp[0]-1][inp[1]-1] is None:
            return -1
        
        if self.round == "X": self.plate[inp[0]-1][inp[1]-1] = "X"
        elif self.round == "O": self.plate[inp[0]-1][inp[1]-1] = "O"
        
        status = self.isWin()
        if self.round == "X": self.round = "O"
        elif self.round == "O": self.round = "X"

        return status


