from src.interface.MyCommand import MyCommand
import logging
import discord
from src.commands.experiment import MyView

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
        prompt_info = {
            'prompt': "((best quality)), ((masterpiece)), (detailed), succubus, ethereal beauty, perched on a cloud, (fantasy illustration:1.3), enchanting gaze, leotard, pantyhose, stockings, bodysuit, captivating pose, delicate wings, otherworldly charm, mystical sky, large moon, moonlit night, soft colors, (detailed cloudscape:1.3), (high-resolution:1.2), from below, (rating_explicit), (score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, high res, 4k)",
            'model': "revAnimated_v2Rebirth.safetensors",
            'negative_prompt': "(nude, thighs, cleavage:1.3), 3d, cartoon, anime, sketches, (worst quality, bad quality, child, cropped:1.4) ((monochrome)), ((grayscale)), (rating_safe), (score_3_up, score_4_up, score_5_up, monochrome, vector art, blurry)",
            'width': 512,
            'height': 768,
            'steps': 30,
            'cfg': 8.5,
            'seed': 123456789
        }
        log.info("Sending response")

        await ctx.send_response(embeds=[embed], view=MyView(), ephemeral=True)
