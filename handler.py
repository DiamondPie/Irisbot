from logger import log, logInfo
from easygoogletranslate import EasyGoogleTranslate
import discord, games, time, asyncio, settings, aiohttp, coinsys, os
from base import *
from typing import Literal

class PoweroffConfirmMenu(discord.ui.View):
    ''' Poweroff confirming ui '''
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Poweroff", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.message.reply("Irisbot will be powered off!")
        log("Bot was powered off remotely.", "Fatal")
        await interaction.client.close()
        return
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.message.reply("Poweroff Cancelled.")
        log("Power off was cancelled.", "Warn")
        self.stop()
        return

def embed_onError(title: str, detail: str) -> discord.Embed:
    error_embed = discord.Embed(title=title, description=detail, colour=settings.theme_color)
    error_embed.set_author(name="Something Unexpected", icon_url="https://cdn-icons-png.flaticon.com/512/4727/4727950.png")
    return error_embed

def embed_onWork(title: str, detail: str) -> discord.Embed:
    work_embed = discord.Embed(title=title, description=detail, colour=settings.theme_color)
    work_embed.set_author(name="Working", icon_url="https://cdn-icons-png.flaticon.com/512/4661/4661833.png")
    return work_embed

def embed_onBusy() -> discord.Embed:
    return discord.Embed(title="There's still a task running in background!", description="Please wait until it finish.", colour=settings.theme_color).set_author(name="Busy", icon_url="https://cdn-icons-png.flaticon.com/512/4572/4572993.png")

def embed_onComplete(title: str, detail: str="") -> discord.Embed:
    return discord.Embed(title=title, description=detail, colour=settings.theme_color).set_author(name="Completed", icon_url="https://cdn-icons-png.flaticon.com/512/4661/4661836.png")

def embed_onIntro(intro_type: "Literal['image_text','image','chat','emoji']", title: str, detail: str="") -> discord.Embed:
    intro_embed = discord.Embed(title=title, description=detail, colour=settings.theme_color)
    if intro_type == "image_text":
        intro_embed.set_author(name="Function", icon_url="https://cdn-icons-png.flaticon.com/512/4620/4620722.png")
    elif intro_type == "image":
        intro_embed.set_author(name="Function", icon_url="https://cdn-icons-png.flaticon.com/512/4808/4808677.png")
    elif intro_type == "chat":
        intro_embed.set_author(name="Function", icon_url="https://cdn-icons-png.flaticon.com/512/4575/4575322.png")
    elif intro_type == "emoji":
        intro_embed.set_author(name="Function", icon_url="https://cdn-icons-png.flaticon.com/512/4811/4811560.png")
    return intro_embed

def embed_onChat(chat: str) -> discord.Embed:
    chat_embed = discord.Embed(description=chat, colour=settings.theme_color)
    chat_embed.set_author(name="Chat", icon_url="https://cdn-icons-png.flaticon.com/512/4548/4548148.png")
    return chat_embed

class Handler(object):
    def __init__(self, client:discord.Client):
        self.rouletteQueue: "dict[discord.abc.MessageableChannel, games.Roulette]" = {}
        self.aiQueue: "list[discord.abc.MessageableChannel]" = []
        self.translator: EasyGoogleTranslate = EasyGoogleTranslate()
        self.chat_model = "gpt"
        self.chat_lang = "en"
        self.client = client
        self.st = time.time()
    
    async def help(self, message: discord.Message, param: "list[str]"=[]):
        ins: "dict[str,dict[str,str]] | None" = read_json("./instructions.json")
        if ins is None: return
        
        if param:
            if param[0] != "__comment" and param[0].lower() in ins.keys():
                content = f"**{param[0].capitalize()}** Commands:"
                for cmd, instruction in ins[param[0].lower()].items():
                    content += f"\n- `{cmd}` {instruction}"
            else:
                content = "Sorry, but we cannot find the category.\nGet the category list by typing `/help`"
        else:
            content = f"**Irisbot v{settings.version} Made by DiamondPie**\n\nCategories of Commands:"
            for typ, cmt in ins["__comment"].items():
                content += f"\n- `{typ.capitalize()}` {cmt}"
            content += "\nType `/help Category` for more info."
        await message.reply(content)

    async def testError(self, message: discord.Message):
        await message.reply("A test error generated!\nYou may see the error at server console,\nor use `/log` to see detail.")
        raise Exception("Don't worry, I am just a test error :)")

    async def getLogInfo(self, message: discord.Message):
        info_embed = discord.Embed(title="Server status", description="Irisbot server debugging data", colour=settings.theme_color)
        h, m, s = map(round,sec_to_time(time.time()-self.st))
        info_embed.add_field(name="Online status", value=f"Server has been online for **{h}h {m}m {s}s**\n**Info: {logInfo.info}\nWarn: {logInfo.warn}\nError: {logInfo.error}**")
        info_embed.set_author(name="Info", icon_url="https://cdn-icons-png.flaticon.com/512/4575/4575303.png")

        if logInfo.recentErrorInfo is None: # 服务端无异常
            info_embed.add_field(name="Errors", value="Woo hoo! No recent Errors!")
        else:
            log_info = f"Recent Error took place at \n**{logInfo.recentErrorInfo['timestamp']}**\n```c++\n{logInfo.recentErrorInfo['traceback']}```"
            if len(log_info) >= 1024: # 如果消息超长则替换错误信息
                log_info = f"Recent Error took place at \n**{logInfo.recentErrorInfo['timestamp']}**\n```Hanc marginis exiguitas non caperet =)```"
            info_embed.add_field(name="Errors", value=log_info)
        
        await message.reply(embed=info_embed)

    async def manual_heartbeat(self, message: discord.Message):
        message_embed = discord.Embed(title="Emergency Manual", description="If the bot goes offline unexpectly...", colour=settings.theme_color)
        message_embed.set_author(name="Info", icon_url="https://cdn-icons-png.flaticon.com/512/4575/4575303.png")
        message_embed.add_field(name="Patient", value="Wait for at most 10 minutes then the bot will reboot.")
        message_embed.add_field(name="Manually reboot", value="You can click on this [link](https://irisbot--diamondpie.repl.co/heartbeat) to reboot the bot.")
        await message.reply(embed=message_embed)
    
    async def quiz(self, message: discord.Message):
        quiz, ans = games.quiz()
        channel = message.channel
        timeout = 60
        before = time.time()
        await message.reply(f"Try this! You have **60** sec.\n**%s**\nUse command `>Answer` E.g. `>2333`" % quiz)
        log("Starting a round of quiz...")
        while True:
            try:
                msg = await self.client.wait_for('message', 
                                                 check=lambda m: m.author == message.author and m.content.startswith(">") and m.channel == channel, 
                                                 timeout=timeout)
            except asyncio.TimeoutError:
                await channel.send(f"Time out!\nThe answer is **{ans}**\nWould you like to try again?")
                log("Quiz terminated because of timed out.")
                break
            else:
                if msg.content[1:] == str(ans):
                    await msg.reply("Congratulations! You did it!")
                    log("Quiz terminated because of player answered correctly.")
                    break
                else:
                    timeout = 60 - (time.time() - before)
                    await msg.reply("Almost there!\nYou have **%.0f secs** left. Quickly!" % timeout)

    async def poweroff(self, message: discord.Message):
        await message.reply("Are you sure want to power off?\n*Irisbot will completely disconnect to discord and cannot be rebooted.*", view=PoweroffConfirmMenu())

    async def qrcode(self, message: discord.Message):
        if not message.attachments:
            await message.reply("Sorry, but no images were found! 😟")
            return
        result = games.analyzeQrcode(message.attachments[0].url)
        result_embed = \
            embed_onError("Qrcode parsing failed!", "Please try to increase the picture resolution and try again.") \
            if result is None \
            else discord.Embed(title="Qrcode successfully analyzed!", description=result, colour=settings.theme_color).set_author(name="Done", icon_url="https://cdn-icons-png.flaticon.com/512/4808/4808825.png")
        await message.reply(embed=result_embed)

    async def roulette(self, message: discord.Message, param: "list[str]"=[]):
        if not message.channel in self.rouletteQueue.keys():
            content = "A new round of Russian roulette begins!\nThis is a 6-shot revolver, loaded with 1 bullet. \n"
            if not param:
                self.rouletteQueue[message.channel] = games.Roulette()
                content += "No firing rewards."
            elif len(param) >= 1:
                self.rouletteQueue[message.channel] = games.Roulette(prize=param[0])
                content += "Firing reward is **"+param[0]+"**."
            elif len(param) >= 2 and param[1] == "once":
                self.rouletteQueue[message.channel] = games.Roulette(prize=param[0],once=True)
                content += "Firing reward is **"+param[0]+"**\n**Once mode**: each player can only play **once**"
            content += "\nUse command `/roulette` to play!"
            await message.reply(content)
            log("Starting a round of roulette...")
        else:
            result = self.rouletteQueue[message.channel].shot(message.author)
            content = f"{message.author.display_name} fired a shot.\n"
            prize = None
            if result is None:
                content += "The gun didn't go off, the next round must be bullets.\n**End of this round of Russian roulette.**"
                del self.rouletteQueue[message.channel]
            elif result:
                content += f"The gun went off.\n**End of this round of Russian roulette.**"
                prize = self.rouletteQueue[message.channel].prize
                log(f"{message.author} won the roulette.")
                del self.rouletteQueue[message.channel]
            else:
                content += f"The gun didn't go off.\n{len(self.rouletteQueue[message.channel].ammo)} rounds left."
            await message.channel.send(content)
            if result and not prize is None:
                await message.reply(f"You won the prize: *{prize}*")
    
    async def paint(self, message: discord.Message, param: "list[str]"=[]):
        if not param:
            message_embed = embed_onIntro("image", "AI Painter Model", "by stability-ai")
            message_embed.add_field(name="Usage", value="```/paint <Prompt> [Negative Prompt]```\n**NOTE: PLEASE USE \"-\" INSTEAD OF SPACE**")
            message_embed.add_field(name="Params", value="**Prompt**: Required, define the scene you would like to draw.\n**Negative Prompt**: Optional, define the object you would NOT like to draw.", inline=False)
            message_embed.add_field(name="Attachment", value="You don't need to upload any attachments.", inline=False)
            await message.reply(embed=message_embed)
            log("Painter returned because of undefined params.")
            return
        elif message.channel in self.aiQueue:
            await message.reply(embed=embed_onBusy())
            log("Painter returned because of repeatly called.")
            return
        
        self.aiQueue.append(message.channel)
        prompt = param[0].replace("-", " ")

        message_embed = embed_onWork("Generating image...", "This may take about 20 secs.\nPlease **DO NOT** send task repeatly.")
        message_embed.add_field(name="**Prompt**", value=prompt)
        negative_prompt = ""
        if len(param) >= 2:
            negative_prompt = param[1].replace("-", " ")
            message_embed.add_field(name="**Negative Prompt**", value=negative_prompt, inline=True)
        log("Img Generating... God bless us.")
        result = await message.reply(embed=message_embed)
        
        data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt
        }

        ts = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.post('http://127.0.0.1:5000/paint', data=data) as response:
                if response.status == 200:
                    response_data: "dict[str, bool|str|None]" = await response.json()
                    if response_data["finished"]:
                        result_embed = embed_onComplete("Image generated successfully!")
                        result_embed.set_image(url=response_data["url"])
                        result_embed.set_footer(text=f"Cost {sec_to_ts(ts)} secs.")
                    else:
                        result_embed = embed_onError("Image generated failure", response_data['error'])
                    await result.edit(content="", embed=result_embed)
                else:
                    await result.edit(content="Uh-oh, it seems that the api doesn't work. :(")
                    log("API Failed, please check if there is something wrong.", "Warn")
                self.aiQueue.remove(message.channel)

    async def text(self, message: discord.Message, param: "list[str]"=[]):
        if not param:
            message_embed = embed_onIntro("image_text", "Bootstrapping Language-Image", "by salesforce")
            message_embed.add_field(name="Usage", value="```/assess <Task> [Addition]```\n**NOTE: PLEASE USE \"-\" INSTEAD OF SPACE**")
            message_embed.add_field(name="Params", value="**Task**: Required, the task type.\n- **image_captioning**: Describe the image.\n- **visual_question_answering**: Answer a question about the image.\n- **image_text_matching**: Matching the similarity of image and text.\n**Addition**: Optional\n- **visual_question_answering**: The question you'd like to ask.\n- **image_text_matching**: The text you'd like to match.", inline=False)
            message_embed.add_field(name="Attachment", value="Upload an image you want to bootstrap.", inline=False)
            await message.reply(embed=message_embed)
            log("Bootstrapping returned because of undefined params.")
            return
        elif not message.attachments:
            await message.reply(embed=embed_onError("Sorry😟", "But no images were found!"))
            return
        elif message.channel in self.aiQueue:
            await message.reply(embed=embed_onBusy())
            log("Bootstrapping returned because of repeatly called.")
            return
        
        self.aiQueue.append(message.channel)
        task = param[0].replace("-", "_")

        message_embed = embed_onWork("Bootstrapping...", "This may take about 1 sec.\nPlease **DO NOT** send task repeatly.")
        message_embed.add_field(name="**Task**", value=task)
        addition = ""
        if len(param) >= 2:
            addition = param[1].replace("-", " ")
            message_embed.add_field(name="**Addition**", value=addition, inline=True)
        log("Bootstrapping... God bless us.")
        result = await message.reply(embed=message_embed)

        data = {
            "img_url": message.attachments[0].url,
            "task": task,
            "addition": addition
        }

        ts = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.post('http://127.0.0.1:5000/text', data=data) as response:
                if response.status == 200:
                    response_data: "dict[str, bool|str|None]" = await response.json()
                    if response_data["finished"]:
                        result_embed = embed_onComplete("Image bootstrapped successfully!", response_data["content"])
                        result_embed.set_footer(text=f"Cost {sec_to_ts(ts)} secs.")
                    else:
                        result_embed = embed_onError("Image bootstrapped failure", response_data['error'])
                    await result.edit(content="", embed=result_embed)
                else:
                    await result.edit(content="Uh-oh, it seems that the api doesn't work. :(")
                    log("API Failed, please check if there is something wrong.", "Warn")
                self.aiQueue.remove(message.channel)
    
    async def face_fix(self, message: discord.Message):
        if not message.attachments:
            message_embed = embed_onIntro("image", "Robust face restoration algorithm", "by sczhou")
            message_embed.add_field(name="Usage", value="```/facefix```")
            message_embed.add_field(name="Params", value="No params.")
            message_embed.add_field(name="Attachment", value="Upload an image you want to fix face.")
            await message.reply(embed=message_embed)
            log("Facefixing returned because of undefined params.")
            return
        elif message.channel in self.aiQueue:
            await message.reply(embed=embed_onBusy())
            log("Facefixing returned because of repeatly called.")
            return
        self.aiQueue.append(message.channel)

        message_embed = embed_onWork("Facefixing...", "This may take around 20 secs.\nPlease **DO NOT** send task repeatly.")
        log("Facefixing... God bless us.")
        result = await message.reply(embed=message_embed)

        data = {
            "img_url": message.attachments[0].url
        }

        ts = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.post('http://127.0.0.1:5000/face', data=data) as response:
                if response.status == 200:
                    response_data: "dict[str, bool|str|None]" = await response.json()
                    if response_data["finished"]:
                        result_embed = embed_onComplete("Face fixed successfully!")
                        result_embed.set_image(url=response_data["url"])
                        result_embed.set_footer(text=f"Cost {sec_to_ts(ts)} secs.")
                    else:
                        result_embed = embed_onError("Face fixed failure", response_data['error'])
                    await result.edit(content="", embed=result_embed)
                else:
                    await result.edit(content="Uh-oh, it seems that the api doesn't work. :(")
                    log("API Failed, please check if there is something wrong.", "Warn")
                self.aiQueue.remove(message.channel)

    async def getExp(self, message: discord.Message):
        if (levelUp := coinsys.dailyExp(message.author.id)):
            await message.author.send(embed=discord.Embed(title="Level up!", description=f"You are now in level {levelUp}", color=settings.theme_color).set_author(name="Note", icon_url="https://cdn-icons-png.flaticon.com/512/4730/4730890.png"))

    async def register(self, message: discord.Message):
        result = coinsys.register(message.author.id)
        if result:
            result_embed = discord.Embed(colour=settings.theme_color)
            result_embed.set_author(name="Registration", icon_url="https://cdn-icons-png.flaticon.com/512/4730/4730870.png")
            result_embed.description = "You have successfully registered an account!\nUse `/profile` to check it."
            result_embed.title = "Account was created!"
        else:
            result_embed = embed_onError("Registration Failed", "You already have an account!")
        await message.reply(embed=result_embed)

    async def profile(self, message: discord.Message, param: "list[str]"=[]):
        result = coinsys.profile(message.author.id)
        if not result[0]:
            await message.reply(embed=embed_onError("Something was lost", "You don't have an account yet!\nUse `/register` to create one!"))
            return
        if not param or len(param) == 1:
            result_embed = discord.Embed(title=str(message.author.display_name),description=result[1][2], colour=result[1][4])
            result_embed.set_author(name="My Profile", icon_url="https://cdn-icons-png.flaticon.com/512/4774/4774695.png")
            result_embed.set_thumbnail(url=str(message.author.display_avatar))
            result_embed.add_field(name="Info", value=f"Level: {result[1][0]}\n{result[1][3]} exp left before level up.")
            result_embed.add_field(name="Score", value=f"Score: {result[1][1]}", inline=True)
        else:
            result = coinsys.change(message.author.id, (key := param[0]), (value := " ".join(param[1:])))
            result_embed = embed_onComplete("Settings took effect", f"The **{key}** of your profile has been set to **{value}**") if result else embed_onError("We didn't find the property", "Maybe you can try for another one?")

        await message.reply(embed=result_embed)

    async def signIn(self, message: discord.Message):
        result, extraScore, signCombo = coinsys.sign_in(message.author.id)
        if not result:
            result_embed = embed_onError("Something was lost", "You don't have an account yet!\nUse `/register` to create one!")
            await message.reply(embed=result_embed)
        elif result == -1:
            result_embed = embed_onError("Tomorrow holds promise", "Don't be anxious, I'll wait for you tomorrow.")
            h, m, s = extraScore
            result_embed.set_footer(text=f"Tomorrow will come up in {h}h {m}m {s}s.")
            await message.reply(embed=result_embed)
        elif result == 1:
            result_embed = discord.Embed(title="Sign-in succeeded", description=f"You have signed in for **{signCombo}** days in a row!\n**Score +3!**", colour=settings.theme_color).set_author(name="1 Sign 1 Day", icon_url="https://cdn-icons-png.flaticon.com/512/4572/4572967.png")
            result_embed.set_footer(text=f"You got {extraScore} more points for your continuous sign-in!" if extraScore else "")
            async with aiohttp.ClientSession() as session:
                async with session.get("http://127.0.0.1:5000/bg") as response:
                    if response.status == 200:
                        response_data: "dict[str, str]" = await response.json()
                        if response_data['finished']:
                            bg_file = discord.File("./cache/bg.jpg", filename="bg.jpg")
                            result_embed.set_image(url="attachment://bg.jpg")
                            await message.reply(file=bg_file, embed=result_embed)

    async def chat_settings(self, message: discord.Message, param: "list[str]"=[]):
        if not param:
            message_embed = embed_onIntro("chat", "ChatAI", "powered by OpenAi/qingyunke/yunxi")
            message_embed.add_field(name="Usage", value="```@Me <Message>``````/chat <Model> [Language]```You don't need to use \"-\" instead of space")
            message_embed.add_field(name="Params", value=f"**Message**: Required, the message.\n**Model**: Required, the chatbot model you want to use.\n- **{'→' if self.chat_model=='gpt' else ''} gpt**: ChatGPT 4.0\n- **{'→' if self.chat_model=='qyk' else ''} qyk**: QingYunKe Chat Model\n**Language**: Optional, output language, not applicable for ChatGPT 4.0\n- **{'→' if self.chat_lang=='en' else ''} en**: English\n- **{'→' if self.chat_lang=='zh' else ''} zh**: Chinese")
            message_embed.add_field(name="Attachment", value="You don't need to upload any attachments.", inline=False)
            await message.reply(embed=message_embed)
            log("Chat settings returned because of undefined params.")
            return
        elif (model := param[0].lower()) in ["gpt", "llama", "qyk"]:
            self.chat_model = model
            if len(param) > 1 and param[1] in ["zh", "en"]:
                self.chat_lang = param[1]
            await message.reply(embed=embed_onComplete("Settings took effect", f"Chatbot Model has been set to **{'llama-2-70b-chat' if model == 'llama' else ''}{'QingYunKe Chat Model' if model == 'qyk' else ''}** with **{self.chat_lang}**"))
        else:
            await message.reply(embed=embed_onError("Unknown Chat Model", "Bot is working hard to grasp the model.."))

    async def chat(self, message: discord.Message):
        msg = message.content[22:].strip()
        
        await message.channel.typing()

        if self.chat_model == "llama":
            data = {
                "prompt": msg
            }

            async with aiohttp.ClientSession() as session:
                async with session.post('http://127.0.0.1:5000/chat', data=data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        if response_data["finished"]:
                            result = response_data['content']
                        else:
                            result = "Think failed\n"+response_data['msg']
                        await message.channel.send(content=result)
                    else:
                        await message.reply(content="Uh-oh, it seems that the api doesn't work. :(")
                        log("API Failed, please check if there is something wrong.", "Warn")

        elif self.chat_model == "gpt":
            async with aiohttp.ClientSession() as session:
                async with session.post(f'http://ovoa.cc/api/Bing.php?msg={msg}&model=down&type=json') as response:
                    if response.status == 200:
                        response_data = await response.json()
                        if response_data["code"] == 200:
                            result = response_data['content']
                        else:
                            result = "Think failed\n"+response_data['msg']
                        await message.channel.send(content=result)
                    else:
                        await message.reply(content="Uh-oh, it seems that the api doesn't work. :(")
                        log("API Failed, please check if there is something wrong.", "Warn")
            # data = {
            #     "api": "56",
            #     "key": settings.yunxi_token,
            #     "text": msg
            # }

            # async with aiohttp.ClientSession() as session:
            #     async with session.post('https://api.a20safe.com/api.php', data=data) as response:
            #         if response.status == 200:
            #             response_data = await response.json()
            #             if response_data["msg"] == "success":
            #                 result = response_data['data'][0]['reply']
            #             else:
            #                 result = "Think failed\n"+response_data['msg']
            #             await message.channel.send(content=result)
            #         else:
            #             await message.reply(content="Uh-oh, it seems that the api doesn't work. :(")
            #             log("API Failed, please check if there is something wrong.", "Warn")
        
        elif self.chat_model == "qyk":
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={self.translator.translate(msg, target_language='zh-CN')}") as response:
                    if response.status == 200:
                        response_data = json.loads(await response.text(encoding='utf-8'))
                        result: str = response_data['content']
                        result = result.replace('菲菲', "IrisBot").replace("{br}", "\n")
                        await message.channel.send(content=self.translator.translate(result, target_language='en') if self.chat_lang=='en' else result)
                    else:
                        await message.reply(content="Uh-oh, it seems that the api doesn't work. :(")
                        log("API Failed, please check if there is something wrong.", "Warn")

    async def leave_message(self, message: discord.Message):
        await message.author.send(embed=embed_onChat(f"Leave you wishes here!\n[Irisbot Message Board](https://irisbot--diamondpie.repl.co/message?user={(name := message.author.name)})"))
        if not os.path.exists(avatar_path := f"./avatar/{name}.png"):
            with open(avatar_path, mode="wb") as a:
                a.write(get(message.author.avatar.url, stream=True).content)

    async def emoji_mix(self, message: discord.Message, param: "list[str]"=[]):
        if not param or len(param[0]) != 2 or len(param) < 2:
            message_embed = embed_onIntro("emoji", "Emoji Kitchen", "Combine 2 emojis into an image")
            message_embed.add_field(name="Usage", value="```/emojimix <Emoji1> <Emoji2>```")
            message_embed.add_field(name="Params", value=f"**Emoji**: Required, the two emojis you want to combine.")
            message_embed.add_field(name="Attachment", value="You don't need to upload any attachments.", inline=False)
            await message.reply(embed=message_embed)
            log("Emoji kitchen returned because of undefined params.")
            return
        elif len(param[0]) <= 2 or len(param[1]) != 1:
            message_embed = embed_onError("Emojis are invalid", "(Did you add more than 1 emojis?)")
            await message.reply(embed=message_embed)
            log("Emoji kitchen returned because of param error.")
            return
        
        emoji_unicode = list(map(emoji_to_unicode, param))

        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://127.0.0.1:5000/emojimix", data={"base": emoji_unicode[0], "extra": emoji_unicode[1]}) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data['finished']:
                        await message.reply(embed=embed_onComplete("").set_image(url=(endpoint := response_data['url'])))
                        log("Emoji kitchen returned as url: "+endpoint)
                    else:
                        log("From Emoji kitchen: unknown error", level="Warn")
                else:
                    await message.reply(content="Uh-oh, it seems that the api doesn't work. :(")
                    log("API Failed, please check if there is something wrong.", "Warn")

    async def dictionary(self, message: discord.Message, param: "list[str]"=[]):
        if not param:
            message_embed = embed_onIntro("chat", "Dictionary", "Search for words here!")
            message_embed.add_field(name="Usage", value="```/dict <word>```")
            message_embed.add_field(name="Param", value="**word**: Required, the word you want to search for.")
            message_embed.add_field(name="Attachments", value="You don't need to upload any attachments.")
            await message.reply(embed=message_embed)
            log("Dictionary returned because of undefined params.")
            return
        
        async with aiohttp.ClientSession(headers={"X-Api-Key": settings.ninjas_token}) as session:
            async with session.get(f"https://api.api-ninjas.com/v1/dictionary?word={param[0]}") as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data["valid"]:
                        message_embed = embed_onComplete("")
                    else:
                        message_embed = embed_onError("")


        
        
