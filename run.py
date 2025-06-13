# https://discord.com/oauth2/authorize?client_id=1304485175660515408&permissions=277025703936&integration_type=0&scope=bot
import discord
import os
import logging
import datetime
import sys
import asyncio
import nest_asyncio
from src.logger import LastNLinesHandler
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed, WebSocketException
from src.commandloader import load_commands
from src.database import initialize_database

from src.comfyutils import all_servers, client_id
import src.comfyuiwatcher as comfyui_watcher

nest_asyncio.apply()

def setup_logger():
    format_string = '%(asctime)s [%(levelname)7s][%(name)15s]  %(message)s'
    logging.Formatter.formatTime = (lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat(sep="T",timespec="milliseconds"))
    logging.basicConfig(
        level=logging.INFO,
        format=format_string,
        stream=sys.stdout
    )
    root_logger = logging.getLogger()
    custom_formatter = logging.Formatter(fmt=format_string)
    handler = LastNLinesHandler()
    handler.setFormatter(custom_formatter)
    root_logger.addHandler(handler)


setup_logger()
log = logging.getLogger(__name__)


async def connect_and_listen(server_address, my_client_id):
    uri = f"ws://{server_address}/ws?clientId={my_client_id}"
    while True:
        try:
            async with connect(uri, max_size=None) as websocket:
                log.info(f"Connected to {server_address}, listening...")
                await comfyui_watcher.listen_for_comfyui_messages(websocket)
        except (ConnectionClosed, WebSocketException, asyncio.TimeoutError) as e:
            if server_address != all_servers.split(",")[0]:
                log.warning(f"WebSocket error with {server_address}: {e}. Reconnecting in 5s...")
        except Exception as e:
            if server_address != all_servers.split(",")[0]:
                log.exception(f"Unexpected error with {server_address}: {e}. Reconnecting in 5s...")
        await asyncio.sleep(5)  # Wait before trying to reconnect


async def start_all_websockets(all_the_servers, my_client_id):
    tasks = []
    for server_address in all_the_servers.split(","):
        tasks.append(asyncio.create_task(connect_and_listen(server_address.strip(), my_client_id)))
    await asyncio.gather(*tasks)


async def main():
    log.info("Initializing database")
    initialize_database()

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
        comfyui_watcher.bot = bot
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"version: {os.getenv('VERSION')}"))

    asyncio.create_task(start_all_websockets(all_servers, client_id))

    # load_listeners("src.listeners", bot)
    load_commands("src.commands", bot)

    log.info("Starting bot")
    await bot.start(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Received exit, shutting down")
    except RuntimeError:
        log.info("Received runtime error, exiting")