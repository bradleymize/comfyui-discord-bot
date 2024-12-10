import json
import logging
import discord

from src.interface.MyCommand import MyCommand
from src.botutils import ComfyUICommand, MyBotInteraction
from src.comfyutils import queue_prompt
from src.database import insert_prompt, update_prompt_id_for_message_id

log = logging.getLogger(__name__)

class Flux(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'flux',
            'description': 'Creates an AI image using ComfyUI (using the flux workflow)'
        }
        self.options = [
            {
                'name': 'prompt',
                'type': discord.SlashCommandOptionType.string,
                'required': True,
                'description': "Describe the image you wish to create"
            },
            {
                'name': 'model',
                'type': discord.SlashCommandOptionType.string,
                'required': True,
                'description': "The model to use",
                'autocomplete': discord.utils.basic_autocomplete(self.get_models)
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
            },
            {
                'name': 'cfg',
                'type': discord.SlashCommandOptionType.number,
                'required': False,
                'default': 1.0,
                'description': "The guidance scale (how closely to follow the prompt). Default: 1.0"
            }
        ]
        self.fn = self.command
        super().register_command()


    def get_models(self, ctx: discord.commands.context.AutocompleteContext):
        models = []
        with open('src/models/flux.json') as f:
            workflow_model_information = json.load(f)
            for model in workflow_model_information:
                models.append(discord.OptionChoice(model['name'], model['value']))
        return models


    async def command(
            self,
            ctx: discord.ApplicationContext,
            prompt: str,
            model: str,
            seed: str = None,
            width: int = 1024,
            height: int = 1024,
            steps: int = 4,
            cfg: float = 1.0
    ):
        log.info("Running basic command")

        log.info("Creating new ComfyUICommand object")
        comfy_ui_command = ComfyUICommand(
            ctx=ctx,
            workflow="flux.json.template",
            prompt=prompt,
            negative_prompt='',
            model=model,
            seed=seed,
            width=width,
            height=height,
            steps=steps,
            cfg=cfg
        )
        values_map = comfy_ui_command.get_values_map()

        await ctx.response.send_message(f"Queueing new image, {ctx.user.mention}")
        response_message = await ctx.interaction.original_response()
        insert_prompt(response_message.id, response_message.channel.id, ctx.user.mention, self.cmd_meta['name'], values_map)

        interaction = await MyBotInteraction.create(bot=self.bot, data=comfy_ui_command)

        queue_response = await queue_prompt(interaction.get_prompt())
        prompt_id = queue_response['prompt_id']
        update_prompt_id_for_message_id(response_message.id, prompt_id)
        log.info("done with flux command")

#         log.info("Calling comfyutils.queue_new_prompt")
#         await ctx.defer()
#         await queue_new_prompt(interaction)
#         interaction_queue.append(interaction)
#
#         queue_status = await get_queue_information()
#         msg = f"""Queued an image with the following config:
# workflow: {values_map['workflow']}
# model: {values_map['model']}
# seed: {values_map['seed']}
# width: {values_map['width']}
# height: {values_map['height']}
# steps: {values_map['steps']}
# cfg: {values_map['cfg']}
# prompt: {values_map['prompt']}
# prompt id: {interaction.prompt_id}
# {queue_status}"""
#
#         response = await ctx.followup.send(msg)
#         interaction.reply_to = response