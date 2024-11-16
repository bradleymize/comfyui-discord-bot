import discord
import logging

import src.comfyui as my_comfyui
from src.botutils import ComfyUICommand, MyBotInteraction, interaction_queue, Reaction

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
        ): # a slash command will be created with the name "comfyui"
            log.info("Creating new ComfyUICommand object")
            comfy_ui_command = ComfyUICommand(
                ctx=ctx,
                prompt=prompt,
                seed=seed,
                width=width,
                height=height,
                steps=steps,
                cfg=1
            )
            values_map = comfy_ui_command.get_values_map()

            interaction = await MyBotInteraction.create(bot=bot, data=comfy_ui_command)
            interaction_queue.append(interaction)

            log.info("Calling comfyui.generate")
            await ctx.defer()

            prompt_id = await my_comfyui.generate(interaction)

            queue_status = await my_comfyui.get_queue_information()
            # TODO: Add workflow to output
            msg = f"""Queued an image with the following config:
seed: {values_map['seed']}
width: {values_map['width']}
height: {values_map['height']}
steps: {values_map['steps']}
prompt: {values_map['prompt']}
prompt id: {prompt_id}
{queue_status}"""

            response = await ctx.followup.send(msg)
            interaction.reply_to = response
