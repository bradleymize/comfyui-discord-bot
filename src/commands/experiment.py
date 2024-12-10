from src.botutils import ComfyUICommand, MyBotInteraction
from src.comfyutils import queue_prompt
from src.interface.MyCommand import MyCommand
import logging
import discord
from src.database import insert_prompt, update_prompt_id_for_message_id

log = logging.getLogger(__name__)


class Experiment(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'experiment',
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

        await ctx.response.send_message(f"Queueing new image, {ctx.user.mention}")
        response_message = await ctx.interaction.original_response()

        comfy_ui_command = ComfyUICommand(
            ctx=ctx,
            workflow="basic.json.template",
            prompt="((best quality)), ((masterpiece)), (detailed), succubus, ethereal beauty, perched on a cloud, (fantasy illustration:1.3), enchanting gaze, leotard, pantyhose, stockings, bodysuit, captivating pose, delicate wings, otherworldly charm, mystical sky, large moon, moonlit night, soft colors, (detailed cloudscape:1.3), (high-resolution:1.2), from below, (rating_explicit), (score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, high res, 4k)",
            negative_prompt="(nude, thighs, cleavage:1.3), 3d, cartoon, anime, sketches, (worst quality, bad quality, child, cropped:1.4) ((monochrome)), ((grayscale)), (rating_safe), (score_3_up, score_4_up, score_5_up, monochrome, vector art, blurry)",
            model="revAnimated_v2Rebirth.safetensors",
            seed=None,
            width=512,
            height=768,
            steps=30,
            cfg=8.5
        )
        values_map = comfy_ui_command.get_values_map()
        insert_prompt(response_message.id, response_message.channel.id, ctx.user.mention, self.cmd_meta['name'], values_map)

        interaction = await MyBotInteraction.create(bot=self.bot, data=comfy_ui_command)

        queue_response = await queue_prompt(interaction.get_prompt())
        prompt_id = queue_response['prompt_id']
        update_prompt_id_for_message_id(response_message.id, prompt_id)
        log.info("done with experiment command")
