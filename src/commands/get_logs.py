from src.logger import LastNLinesHandler
from src.interface.MyCommand import MyCommand
import logging
import discord
import os

log = logging.getLogger(__name__)

class GetLogs(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'get-logs' if os.getenv("BOT_TYPE") == 'PRODUCTION' else 'dev-get-logs',
            'description': 'Retrieves the last 100 log statements'
        }
        self.options = []
        self.fn = self.command
        super().register_command()


    async def command(
            self,
            ctx: discord.ApplicationContext
    ):
        lastNLinesHandler = None
        for handler in log.parent.handlers:
            if isinstance(handler, LastNLinesHandler):
                lastNLinesHandler = handler

        message = "Unable to get the lines from the logger"

        if lastNLinesHandler is not None:
            lines = lastNLinesHandler.get_last_n_lines()
            max_allowed_lines = lines[len(lines) - 1975:]
            message = f"```\n{max_allowed_lines}\n```"

        if ctx.user.id == 185542644850622464:
            await ctx.send_response(message, ephemeral=True)
        else:
            await ctx.send_response("Not authorized to view the logs", ephemeral=True)
