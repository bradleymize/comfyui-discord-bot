# https://discord.com/oauth2/authorize?client_id=1304485175660515408&permissions=277025703936&integration_type=0&scope=bot

import discord
import dotenv
import os

from src.bot import Bot as MyBot
from src.command import Command

def main():
    cmd = Command()

    print("Loading environment")
    dotenv.load_dotenv()

    bot_type = os.getenv("BOT_TYPE")
    if bot_type is None:
        bot_type = "DEVELOPMENT"
    token_name = f"{bot_type}_BOT_TOKEN"
    print(f"loading: {token_name}")

    token = str(os.getenv(token_name))

    print("Creating bot")
    if bot_type == "DEVELOPMENT":
        bot = discord.Bot(debug_guilds=[185544950014935040])
    else:
        bot = discord.Bot()

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online!")

    cmd.initialize(bot)

    print("Starting bot")
    bot.run(token)


if __name__ == "__main__":
    main()