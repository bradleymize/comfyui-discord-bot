import json
import logging
import discord
import random
import os

from src.interface.MyCommand import MyCommand
from src.botutils import ComfyUICommand, get_and_fill_template
from src.comfyutils import queue_prompt, get_sampler_names, get_schedulers, post_image
from src.database import insert_prompt, update_prompt_id_for_message_id

log = logging.getLogger(__name__)

class Anime(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'anime' if os.getenv("BOT_TYPE") == 'PRODUCTION' else 'dev-anime',
            'description': 'Converts an image to anime style (takes anywhere from 30 sec - 2 min)'
        }
        self.options = [
            {
                'name': 'name',
                'type': discord.SlashCommandOptionType.string,
                'required': True,
                'description': "What to call this image / existing uploaded image to use"
            },
            {
                'name': 'image',
                'type': discord.SlashCommandOptionType.attachment,
                'required': False,
                'default': None,
                'description': "Image to upload. Reference it in the future by the name provided"
            },
            {
                'name': 'prompt',
                'type': discord.SlashCommandOptionType.string,
                'required': False,
                'default': None,
                'description': "Describe what you want the image to contain (roughly, not many changes are allowed)"
            },
            {
                'name': 'negative_prompt',
                'type': discord.SlashCommandOptionType.string,
                'required': False,
                'default': None,
                'description': "Describe what you DON'T want the image to contain"
            },
            {
                'name': 'seed',
                'type': discord.SlashCommandOptionType.string,
                'required': False,
                'default': None,
                'description': "Number used to help re-create images. Default: (random)"
            },
            {
                'name': 'strength',
                'type': discord.SlashCommandOptionType.number,
                'required': False,
                'default': None,
                'description': "1 = most freedom, 30 = original image. Recommend no more than 15. Default: 8"
            }
        ]
        self.fn = self.command
        super().register_command()


    async def command(
            self,
            ctx: discord.ApplicationContext,
            name: str,
            image: discord.Attachment = None,
            prompt: str = None,
            negative_prompt: str = None,
            seed: str = None,
            strength: float = None,
    ):
        log.info("Running anime command")

        if image is not None:
            try:
                await post_image(name, image)
            except Exception as e:
                log.error(str(e))
                await ctx.send_response("Error uploading image", ephemeral=True)
                return


        if seed is None:
            seed = random.getrandbits(64)
        else:
            seed = int(seed)
        values_map = {
            'name': name,
            'workflow': 'anime.json.template',
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'seed': seed,
            'strength': strength or 8
        }

        await ctx.response.send_message(f"Converting image, {ctx.user.mention}")
        response_message = await ctx.interaction.original_response()
        insert_prompt(response_message.id, response_message.channel.id, ctx.user.mention, self.cmd_meta['name'], values_map)

        prompt_config = get_and_fill_template(values_map)
        prompt = json.loads(prompt_config)

        queue_response = await queue_prompt(prompt)
        prompt_id = queue_response['prompt_id']
        update_prompt_id_for_message_id(response_message.id, prompt_id)
        log.info("done with anime command")
