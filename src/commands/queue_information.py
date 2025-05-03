from src.comfyutils import get_queue_information
from src.interface.MyCommand import MyCommand
import logging
import discord
import os

log = logging.getLogger(__name__)

class QueueInformation(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'queue-information' if os.getenv("BOT_TYPE") == 'PRODUCTION' else 'dev-queue-information',
            'description': 'Retrieves information about the comfyui queue'
        }
        self.options = []
        self.fn = self.command
        super().register_command()


    async def command(
            self,
            ctx: discord.ApplicationContext
    ):
        await ctx.send_response(await get_queue_information(), ephemeral=True)
