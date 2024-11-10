# https://discord.com/oauth2/authorize?client_id=1304485175660515408&permissions=277025703936&integration_type=0&scope=bot
import discord
import dotenv
import os
import logging
import datetime
import sys
import asyncio
import nest_asyncio
from websockets.asyncio.client import connect

import src.version
from src.command import Command
from src.comfyui import server_address, client_id
import src.comfyuiwatcher as comfyui_watcher

nest_asyncio.apply()

async def main():
    setup_logger()
    log = logging.getLogger(__name__)

    cmd = Command()

    log.info("Loading environment")
    dotenv.load_dotenv()

    bot_type = os.getenv("BOT_TYPE")
    if bot_type is None:
        bot_type = "DEVELOPMENT"
    token_name = f"{bot_type}_BOT_TOKEN"
    log.info(f"loading: {token_name}")

    token = str(os.getenv(token_name))

    log.info("Creating bot")
    if bot_type == "DEVELOPMENT":
        bot = discord.Bot(debug_guilds=[185544950014935040])
    else:
        bot = discord.Bot()

    @bot.event
    async def on_ready():
        log.info(f"{bot.user} is ready and online!")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"version: {src.version.VERSION}"))


    log.info("connecting to websocket")
    async with connect("ws://{}/ws?clientId={}".format(server_address, client_id), max_size=None) as websocket:
        log.info("Starting long-term websocket watcher")
        asyncio.ensure_future(comfyui_watcher.listen_for_comfyui_messages(websocket))

        cmd.initialize(bot, websocket)
        log.info("Starting bot")
        bot.run(token)


def setup_logger():
    logging.Formatter.formatTime = (lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat(sep="T",timespec="milliseconds"))
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)7s][%(name)15s]  %(message)s',
        stream=sys.stdout
    )

if __name__ == "__main__":
    asyncio.run(main())