import discord, time, asyncio, settings, traceback

from discord.flags import Intents
from py_switch import Switch
from logger import log
from handler import Handler
from api import entry
from keep_alive import start_heartbeat

async def send_direct_message(user: discord.User, message: str):
    await user.send(message)

class IrisClient(discord.Client):  
    handle: "Handler|None" = None
    disconnect_time = 0
    ts_before = time.time()
    
    async def on_ready(self) -> None:
        log(f"{self.user} is running on status \033[1m{self.status.name}\033[0m.")
        log("Powering on cost \033[4m%.2f\033[0m secs." % (time.time()-self.ts_before))
        log("Heartbeat latency: \033[4m%.2f\033[0m secs." % self.latency)
        log(f"Server Version: \033[4m{settings.version}\033[0m")
        log(f"Framework Version: \033[4m{discord.__version__}\033[0m")
        if not settings.endpoint:
            log("HTTP API not configured, port transaction is unavailable.", "Warn")
        else:
            log(f"Using HTTP transaction on http://{settings.endpoint['host']}:{settings.endpoint['port']}")
        # log(f"## {quote()} ##")

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user: return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        log(f"Message from {username} on {channel}: {user_message}")
        await self.handle.getExp(message)

        try:
            if user_message.startswith(settings.command_prefix):
                command: str = (msg_processed := user_message.split())[0][1:]
                param: list = msg_processed[1:]
                with Switch(command) as case:
                    if case("test"):
                        await message.channel.send(f"Test Message sent at %s" % time.ctime())
                    if case("pritest"):
                        await message.author.send(f"Test DM sent at %s" % time.ctime())
                    if case("log"):
                        await self.handle.getLogInfo(message)
                    if case("testerror"):
                        await self.handle.testError(message)
                    if case("poweroff"):
                        await self.handle.poweroff(message)
                    if case("help"):
                        await self.handle.help(message, param)
                    if case("quiz"):
                        await self.handle.quiz(message)
                    if case("qrcode"):
                        await self.handle.qrcode(message)
                    if case("roulette"):
                        await self.handle.roulette(message, param)
                    if case("paint"):
                        await self.handle.paint(message, param)
                    if case("assess"):
                        await self.handle.text(message, param)
                    if case("facefix"):
                        await self.handle.face_fix(message)
                    if case("kht"):
                        await message.reply("[Kahoot](https://kahoot.it/)")
                    if case("manual"):
                        await self.handle.manual_heartbeat(message)
                    if case("register"):
                        await self.handle.register(message)
                    if case("profile"):
                        await self.handle.profile(message, param)
                    if case("sign"):
                        await self.handle.signIn(message)
                    if case("chat"):
                        await self.handle.chat_settings(message, param)
                    if case("type"):
                        print(message.channel.type)
                    if case("avatar"):
                        print(message.author.avatar.url)
                        print(message.author.nick)
                        print(message.author.name)
                    if case("leavemsg"):
                        await self.handle.leave_message(message)
                    if case("emojimix"):
                        await self.handle.emoji_mix(message, param)
            elif user_message.startswith(f"<@{self.user.id}>"):
                await self.handle.chat(message)
                    
        except Exception as ex:
            log(f"[{ex.__traceback__.tb_lineno}] {type(ex).__name__}: {ex}", "Error", traceback=traceback.format_exc())

    async def on_disconnect(self) -> None:
        self.disconnect_time += 1
        log(f"Bot has been disconnected from discord: {self.disconnect_time}", "Fatal")
        log("Trying to reconnect...", "Info")

    async def on_error(self, event: str, t) -> None:
        log(f"An uncaught error occurred at \033[4m{event}\033[0m\n{t}", "Error", traceback=t)

def run():
    log("Irisbot Made by DiamondPie")
    st = time.time()
    log("Loading default intents...")
    intents = discord.Intents.default()
    log(f"Configuring intents... {intents}")
    intents.message_content = settings.message_content
    intents.members = settings.members
    log("Instantiating bot client...")
    client: discord.Client = IrisClient(intents=intents)
    log("Setting event handler...")
    client.handle = Handler(client)
    log(f"Running bot client: {client}")
    entry()
    log("Starting api in thread...")
    if settings.heartbeat:
        start_heartbeat()
        log("Starting heartbeat in thread...")
    else:
        log("Heartbeat is disabled. If it is not expected, go to settings.py and set heartbeat to True", "Warn")
    log("Startup completed! Cost %.2f secs." % (time.time()-st))
    log("See gateway log below for more information.")
    client.run(settings.discord_token)
    log("Process was terminated manually.", "Fatal")