import discord
import logging
import os

import src.comfyui as my_comfyui
from src.botutils import ComfyUICommand, MyBotInteraction, interaction_queue, is_valid_reaction, Reaction

log = logging.getLogger(__name__)


class Command:
    def initialize(self, bot, websocket):

        def get_workflows(ctx: discord.commands.context.AutocompleteContext):
            package_dir = "src/workflows"
            files = os.listdir(package_dir)
            return files

        log.info("Initializing comfyui command")

        @bot.command(description="Creates an AI image using ComfyUI") # this decorator makes a slash command
        @discord.option("prompt", type=discord.SlashCommandOptionType.string, required=True, description="Describe the image you wish to create")
        @discord.option("workflow", type=discord.SlashCommandOptionType.string, required=True, description="The workflow to use for generating the image", default="default.json.template", autocomplete=discord.utils.basic_autocomplete(get_workflows))
        @discord.option("seed", type=discord.SlashCommandOptionType.string, required=False, description="Number used to help re-create images. Default: (random)")
        @discord.option("width", type=discord.SlashCommandOptionType.integer, required=False, description="The desired width of the generated image. Default: 1024")
        @discord.option("height", type=discord.SlashCommandOptionType.integer, required=False, description="The desired height of the generated image. Default: 1024")
        @discord.option("steps", type=discord.SlashCommandOptionType.integer, required=False, description="The number of iterations to perform when generating the image. Default: 4")
        async def comfyui(
                ctx: discord.ApplicationContext,
                prompt: str,
                workflow: str,
                seed: str,
                width: int,
                height: int,
                steps: int
        ): # a slash command will be created with the name "comfyui"
            log.info("Creating new ComfyUICommand object")
            comfy_ui_command = ComfyUICommand(
                ctx=ctx,
                workflow=workflow,
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
            msg = f"""Queued an image with the following config:
workflow: {values_map['workflow']}
seed: {values_map['seed']}
width: {values_map['width']}
height: {values_map['height']}
steps: {values_map['steps']}
prompt: {values_map['prompt']}
prompt id: {prompt_id}
{queue_status}"""

            response = await ctx.followup.send(msg)
            interaction.reply_to = response


        @bot.listen
        async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
            log.info(f"Processing reaction: {payload.emoji.name}")

            if is_valid_reaction(payload, bot.user.id):

                if payload.emoji.name == Reaction.REPEAT.value:
                    # emoji is a supported reaction
                    interaction = await MyBotInteraction.create(bot=bot, data=payload)
                    if isinstance(interaction.values_map, dict):
                        log.info("queueing prompt stuff")
                        await my_comfyui.queue_new_prompt(interaction)
                        status = await my_comfyui.get_queue_information()
                        await interaction.reply_to.channel.send(f"{interaction.mention.mention}, regenerating the image with a new seed... {status}")
                    else:
                        log.warning("Message is not one that can regenerate stuff")
                elif payload.emoji.name == Reaction.DELETE.value:
                    interaction = await MyBotInteraction.create(bot=bot, data=payload)
                    await interaction.message.delete()
            else:
                log.info(f"{payload.emoji.name} is not a supported reaction or added by bot, ignoring")


        @bot.command(description="Lists the available workflows")
        async def workflows(
                ctx: discord.ApplicationContext,
                workflow: str
        ):
            log.info(f"Got workflow: {workflow}")
            await ctx.respond(f"Selected {workflow}", ephemeral=True)