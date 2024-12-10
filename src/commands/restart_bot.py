from src.interface.MyCommand import MyCommand
import logging
import discord
from src.views.ImageResponseView import ImageResponseView

log = logging.getLogger(__name__)


class RestartBot(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'restart-bot',
            'description': "If the buttons aren't working, run this command"
        }
        self.options = []
        self.fn = self.command
        super().register_command()


    async def command(
            self,
            ctx: discord.ApplicationContext,
    ):
        log.info("Running restart-bot command")

        embed = discord.Embed(
            image="https://b-rad.dev/images/ai/revanimated-rebirth-v2/sample-01.png",
            color=int("0x3498db", 16)
        )
        log.info("Sending response")

        await ctx.send_response(embeds=[embed], view=ImageResponseView(), ephemeral=True)
