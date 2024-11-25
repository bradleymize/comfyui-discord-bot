from src.commands.interface.MyCommand import MyCommand
import discord

class TestTwo(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        print("Initializing Test 2 - test2 command")
        self.bot.command(name="test2", description="Simple command")(self.command)


    async def command(self, ctx: discord.ApplicationContext):
        print("Inside Test 2 - command")
        await ctx.respond("NOT Test 1, but Test 2")