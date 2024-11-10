import discord
import random
import logging
import asyncio

import src.bot as my_bot
import src.comfyui as my_comfyui

log = logging.getLogger(__name__)


class Command:
    def initialize(self, bot, websocket):

        log.info("Initializing comfyui command")

        @bot.command(description="Creates an AI image using ComfyUI") # this decorator makes a slash command
        # @discord.option("workflow", type=discord.SlashCommandOptionType.string, required=True)
        @discord.option("prompt", type=discord.SlashCommandOptionType.string, required=True)
        @discord.option("seed", type=discord.SlashCommandOptionType.integer, required=False)
        @discord.option("width", type=discord.SlashCommandOptionType.integer, required=False)
        @discord.option("height", type=discord.SlashCommandOptionType.integer, required=False)
        @discord.option("steps", type=discord.SlashCommandOptionType.integer, required=False)
        async def comfyui(
                ctx: discord.ApplicationContext,
                # workflow: str,
                prompt: str,
                seed: int,
                width: int,
                height: int,
                steps: int
        ): # a slash command will be created with the name "ping"
            req = my_bot.process_request(ctx)
            if seed is None:
                seed = random.getrandbits(64)
            if width is None:
                width = 1024
            if height is None:
                height = 1024
            if steps is None:
                steps = 4

            values_map = {
                'seed': seed,
                'width': width,
                'height': height,
                'steps': steps,
                'cfg': 1,
                'prompt': prompt
            }

            log.info("Calling comfyui.generate")
            await ctx.defer()
            # await req['channel'].send(msg)

            prompt_id = await my_comfyui.generate(ctx, websocket, None, values_map)

            queue_status = await my_comfyui.get_queue_information()
            msg = f"""Queued an image with the following config:
seed: {seed}
width: {width}
height: {height}
steps: {steps}
prompt: {prompt}
prompt id: {prompt_id}
{queue_status}"""

            response = await ctx.followup.send(msg)
            req['response'] = response

            # log.info("sending image buffer response")
            # await ctx.followup.send(files=image_buffer_list)
            # await req['channel'].send(files=image_buffer_list)

            # log.debug(f"queue before: {my_bot.message_queue}")
            # my_bot.delete_message(ctx.interaction.id)
            # log.debug(f"queue after: {my_bot.message_queue}")