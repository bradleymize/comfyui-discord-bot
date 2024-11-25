from src.commands.interface.MyCommand import MyCommand
import discord

class TestOne(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        print("Initializing Test 1 - test1 command")
        self.bot.command(name="test1", description="Simple command")(self.command)


    async def command(self, ctx: discord.ApplicationContext):
        print("Inside Test 1 - command")
        await ctx.respond("Test 1")