import json

from src.comfyutils import get_sampler_names, get_schedulers
from src.interface.MyCommand import MyCommand
import logging
import discord
import os

log = logging.getLogger(__name__)


class Experiment(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'experiment' if os.getenv("BOT_TYPE") == 'PRODUCTION' else 'dev-experiment',
            'description': 'Command to test experimental features'
        }
        self.options = []
        self.fn = self.command
        super().register_command()


    async def command(
            self,
            ctx: discord.ApplicationContext,
    ):
        log.info("Running experimental command")

        samplers = await get_sampler_names()
        schedulers = await get_schedulers()

        msg = f"Samplers:\n```\n{json.dumps(samplers, indent=4)}\n```\nSchedulers:\n```\n{json.dumps(schedulers, indent=2)}\n```"

        await ctx.response.send_message(msg, ephemeral=True)
