from src.commands.interface.MyCommand import MyCommand
import os
import logging
import discord
from src.botutils import ComfyUICommand, MyBotInteraction, interaction_queue
from src.comfyutils import queue_new_prompt, get_queue_information

log = logging.getLogger(__name__)

class ComfyUI(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'comfyui',
            'description': 'Creates an AI image using ComfyUI'
        }
        self.options = [
            {
                'name': 'prompt',
                'type': discord.SlashCommandOptionType.string,
                'required': True,
                'description': "Describe the image you wish to create"
            },
            {
                'name': 'workflow',
                'type': discord.SlashCommandOptionType.string,
                'required': True,
                'description': "The workflow to use for generating the image",
                'default': "default.json.template",
                'autocomplete': discord.utils.basic_autocomplete(self.get_workflows)
            },
            {
                'name': 'seed',
                'type': discord.SlashCommandOptionType.string,
                'required': False,
                'default': None,
                'description': "Number used to help re-create images. Default: (random)"
            },
            {
                'name': 'width',
                'type': discord.SlashCommandOptionType.integer,
                'required': False,
                'default': 1024,
                'description': "The desired width of the generated image. Default: 1024"
            },
            {
                'name': 'height',
                'type': discord.SlashCommandOptionType.integer,
                'required': False,
                'default': 1024,
                'description': "The desired height of the generated image. Default: 1024"
            },
            {
                'name': 'steps',
                'type': discord.SlashCommandOptionType.integer,
                'required': False,
                'default': 4,
                'description': "The number of iterations to perform when generating the image. Default: 4"
            }
        ]
        self.fn = self.command
        super().register_command()


    def get_workflows(self, ctx: discord.commands.context.AutocompleteContext):
        package_dir = "src/workflows"
        files = os.listdir(package_dir)
        return files


    async def command(
            self,
            ctx: discord.ApplicationContext,
            prompt: str,
            workflow: str = "default.json.template",
            seed: str = None,
            width: int = 1024,
            height: int = 1024,
            steps: int = 4
    ):
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

        interaction = await MyBotInteraction.create(bot=self.bot, data=comfy_ui_command)

        log.info("Calling comfyutils.queue_new_prompt")
        await ctx.defer()
        await queue_new_prompt(interaction)
        interaction_queue.append(interaction)

        queue_status = await get_queue_information()
        msg = f"""Queued an image with the following config:
workflow: {values_map['workflow']}
seed: {values_map['seed']}
width: {values_map['width']}
height: {values_map['height']}
steps: {values_map['steps']}
prompt: {values_map['prompt']}
prompt id: {interaction.prompt_id}
{queue_status}"""

        response = await ctx.followup.send(msg)
        interaction.reply_to = response