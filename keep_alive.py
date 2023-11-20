from flask import Flask, jsonify, redirect, render_template, send_file, request
from threading import Thread
from flask_cors import CORS
from time import ctime
from logger import log
import json

app = Flask('', template_folder="message")
CORS(app)
DESCRIPTION = """Irisbot is a powerful and native bot of Discord Group Chat<br/>
- >> <a href="https://discordapp.com/users/1125178615122907295">My Discord</a> <<<br/>
- >> QQ 2957423896 << <br/>
- >> <a href="http://irisbot.web3v.vip">Offical Website</a> <<<br/>
- >> <a href="https://discord.com/api/oauth2/authorize?client_id=1162215111352647771&permissions=2183991392320&scope=bot">Invite The Bot</a> <<
"""

@app.route('/')
def mainpage(): 
    ''' 不带终结点，重定向至主网页 '''
    return redirect("http://irisbot.web3v.vip", code=302)

@app.route('/heartbeat')
def home():
    ''' 心跳路由 '''
    log(f"Heartbeat at {(ts := ctime())}")
    return jsonify({
        "success": True,
        "heartbeat": "GET",
        "timestamp": ts
    })

@app.route("/des")
def description():
    return DESCRIPTION

@app.route("/message", methods=['GET'])
def message():
    ''' 由用户发起，返回留言板网页 '''
    user = str(request.args.get("user")) # 获得用户名
    with open("./message/data.json", mode='r') as f:
        dat: "dict[str, list[str]]" = json.load(f) # 获得评论记录

    preview = "" # 评论的html标签
    flag = 1
    for username, content in dat.items():
        if flag >= 5: break
        preview += f"""<div class="message">
                <div class="message-info">
                    <div class="info">
                        <img src="./get_avatar?name={username}" alt="avatar" width="50" height="50">
                        <strong>{username}</strong>
                    </div>
                    <span>{content[0]}</span>
                </div>
                <div class="content">
                    {content[1]}
                </div>
            </div>"""
        flag += 1
    return render_template("leavemsg.html", usrname=user, preview=preview)

@app.route("/receive", methods=['POST'])
def receive():
    try:
        received = request.get_json()
        username, ts, content = received.get("username"), received.get("timestamp"), received.get("content")
        DATA = "./message/data.json"
        with open(DATA, mode='r') as f:
            before: "dict[str, list[str]]" = json.load(f)
        if username in before.keys():
            before[username][0] = ts
            before[username][1] = content
            dat = before
        else:
            dat = {username: [ts, content], **before}

        with open(DATA, mode='w') as f:
            json.dump(dat, f, indent=4)
    except Exception as ex:
        return jsonify({
            "success": False,
            "error": ex
        })
    else:
        return jsonify({
            "success": True,
            "error": None
        })

@app.route("/finish")
def finish():
    return render_template("finish.html")

@app.route("/get_avatar")
def get_avatar():
    name = str(request.args.get("name"))
    return send_file(f"./avatar/{name}.png", mimetype="image/png")

def run():
    app.run(host="0.0.0.0", port=13579)

def start_heartbeat():
    log("Heartbeat Starts on http://0.0.0.0:13579")
    t = Thread(target=run, daemon=False)
    t.start()

def debug():
    app.run(host="127.0.0.1", port="8080")

if __name__ == "__main__":
    debug()
