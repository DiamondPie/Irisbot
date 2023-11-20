from requests import get
from logger import log
import json, time, traceback

def quote():
    q = get("https://v.api.aa1.cn/api/api-wenan-anwei/index.php?type=json", timeout=5).content.decode("utf-8")
    if not q: return ""
    return json.loads(q)["anwei"]

def read_json(path: str):
    try:
        with open(path, mode="r") as f: return json.load(f)
    except Exception as ex:
        log(f"[{ex.__traceback__.tb_lineno}]: {ex}", "Error", traceback=traceback.format_exc())
        return None

def write_json(path: str, value):
    try:
        with open(path, mode="w") as f: json.dump(value, f, indent=4, ensure_ascii=False)
    except Exception as ex:
        log("Error occured while writing data", "Warn")
        raise
    
def sec_to_time(s):
    ''' Input a sec, return time (HH:MM:SS) '''
    return [s // 3600, s // 60 % 60, s % 60]

def sec_to_ts(ts):
    ''' Input a timestamp, return timedelta '''
    return round(time.time()-ts, 2)

def emoji_to_unicode(emoji: str):
    assert len(emoji) == 1, "Emoji imvalid!"
    return emoji.encode('unicode-escape').decode('utf-8')[-5:]
