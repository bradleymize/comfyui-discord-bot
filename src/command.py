import discord
import random
import logging

import src.bot as my_bot
import src.comfyui as my_comfyui

log = logging.getLogger(__name__)


class Command:
    def initialize(self, bot, websocket):

        log.info("Initializing comfyui command")

        @bot.command(description="Creates an AI image using ComfyUI") # this decorator makes a slash command
        # @discord.option("workflow", type=discord.SlashCommandOptionType.string, required=True)
        @discord.option("prompt", type=discord.SlashCommandOptionType.string, required=True, description="Describe the image you wish to create")
        @discord.option("seed", type=discord.SlashCommandOptionType.string, required=False, description="Number used to help re-create images. Default: (random)")
        @discord.option("width", type=discord.SlashCommandOptionType.integer, required=False, description="The desired width of the generated image. Default: 1024")
        @discord.option("height", type=discord.SlashCommandOptionType.integer, required=False, description="The desired height of the generated image. Default: 1024")
        @discord.option("steps", type=discord.SlashCommandOptionType.integer, required=False, description="The number of iterations to perform when generating the image. Default: 4")
        async def comfyui(
                ctx: discord.ApplicationContext,
                # workflow: str,
                prompt: str,
                seed: str,
                width: int,
                height: int,
                steps: int
        ): # a slash command will be created with the name "ping"
            req = my_bot.process_request(ctx)
            if seed is None:
                seed_num = random.getrandbits(64)
            else:
                seed_num = int(seed) # TODO: error handling
            if width is None:
                width = 1024
            if height is None:
                height = 1024
            if steps is None:
                steps = 4

            prompt = prompt.replace("\"", "\\\"")

            values_map = {
                'seed': seed_num,
                'width': width,
                'height': height,
                'steps': steps,
                'cfg': 1,
                'prompt': prompt
            }

            log.info("Calling comfyui.generate")
            await ctx.defer()

            prompt_id = await my_comfyui.generate(ctx, None, values_map)

            queue_status = await my_comfyui.get_queue_information()
            msg = f"""Queued an image with the following config:
seed: {seed_num}
width: {width}
height: {height}
steps: {steps}
prompt: {prompt}
prompt id: {prompt_id}
{queue_status}"""

            response = await ctx.followup.send(msg)
            req['response'] = response
