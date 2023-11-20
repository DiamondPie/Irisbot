from flask import Flask, jsonify, request
import replicate, settings, threading
from requests import get

app = Flask(__name__)

# 实例化一个replicate客户端，超时30秒
rep = replicate.Client(api_token=settings.replicate_token, timeout=30)

@app.route('/paint', methods=['POST'])
def paint():
    try:
        prompt = request.form["prompt"] # 输入参数
        negative_prompt = request.form["negative_prompt"] # 排除参数
        output = rep.run(
            "stability-ai/sdxl:c221b2b8ef527988fb59bf24a8b97c4561f1c671f73bd389f866bfb27c061316",
            input={
                "prompt": prompt,
                "negative_prompt": negative_prompt
            }
        )
    except Exception as ex:
        # 出现异常，返回错误信息
        return jsonify({
            "finished": False,
            "url": None,
            "error": str(ex)
        })
    else:
        return jsonify({
            "finished": True,
            "url": output[0],
            "error": None
        })
    
@app.route('/text', methods=['POST'])
def text():
    try:
        img = request.form["img_url"] # 图片直链
        task = request.form["task"] # 任务类型
        
        data = {
            "image": img,
            "task": task
        }
        
        # 通过任务类型，传入合适的附加参数
        data["question" if task=="visual_question_answering" else "caption" if task=="image_text_matching" else ""] = request.form["addition"]
        # print(data)
        
        output = rep.run(
            "salesforce/blip:2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746",
            input=data
        )

        result: str = str(output)
    except Exception as ex:
        # 出现异常，返回错误信息
        return jsonify({
            "finished": False,
            "content": None,
            "error": str(ex)
        })
    else:
        return jsonify({
            "finished": True,
            "content": result,
            "error": None
        })

@app.route('/face', methods=['POST'])
def face():
    try:
        img_url = request.form["img_url"] # 图片直链
        output = rep.run(
            "sczhou/codeformer:7de2ea26c616d5bf2245ad0d5e24f0ff9a6204578a5c876db53142edd9d2cd56",
            input = {
                "image": img_url
            }
        )

    except Exception as ex:
        # 出现异常，返回错误信息
        return jsonify({
            "finished": False,
            "url": None,
            "error": str(ex)
        })
    else:
        return jsonify({
            "finished": True,
            "url": output,
            "error": None
        })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        prompt = request.form["prompt"]
        output = rep.run(
            "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
            input = {
                "prompt": prompt
            }
        )
        result = ""
        for item in output: result += item

    except Exception as ex:
        return jsonify({
            "finished": False,
            "content": None,
            "error": str(ex)
        })
    else:
        return jsonify({
            "finished": True,
            "content": result,
            "error": None
        })
    
@app.route("/bg")
def background():
    # 获取签到图片背景

    img = get(
        "https://iw233.cn/api.php?sort=pc",
        headers={
            "Referer": "https://weibo.com/"
        }
    )
    
    # 将图片写入缓存
    with open("./cache/bg.jpg", mode="wb") as f:
        f.write(img.content)
        
    return jsonify({
        "finished": True
    })

@app.route("/emojimix", methods=['POST'])
def emojimix():
    emoji_list = [request.form["base"], request.form["extra"]]
    emoji_list_both = [emoji_list, list(reversed(emoji_list))]
    DATE = ("20201001", "20230301", "20210521")

    for date in DATE:
        for e1, e2 in emoji_list_both:
            if get(url := f"https://www.gstatic.com/android/keyboard/emojikitchen/{date}/u{e1}/u{e1}_u{e2}.png").status_code == 200:
                return jsonify({
                    "finished": True,
                    "url": url
                })
        
    return jsonify({
        "finished": False,
        "url": None
    })

def start():
    app.run()

def entry():
    t = threading.Thread(target=start)
    t.setDaemon(True)
    t.start()

if __name__ == "__main__":
    start()