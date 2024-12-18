import json
from collections import namedtuple
import discord
import random

from src.botutils import ComfyUICommand, get_and_fill_template
from src.comfyutils import queue_prompt
from src.commands.experiment import log
from src.database import get_prompt_information_for_message_id, insert_prompt, update_prompt_id_for_message_id, \
    delete_prompt_information_for_message_id


class ImageResponseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        style=discord.ButtonStyle.primary,
        custom_id="image:regenerate",
        emoji="🔁",
        label="Regenerate"
    )
    async def regenerate_callback(self, button, interaction):
        prompt_info = get_prompt_information_for_message_id(interaction.message.id)
        if prompt_info is None:
            await interaction.response.send_message("Unable to retrieve prompt information for generating a new image", ephemeral=True)
            return

        await interaction.response.send_message("Working on new generation...")
        response_message = await interaction.original_response()

        command_name = prompt_info.command_name

        prompt_values = json.loads(prompt_info.prompt_values)
        prompt_values['seed'] = None

        if command_name == 'anime':
            values_map = {k: v for k, v in prompt_values.items() if v is not None}
            values_map['seed'] = random.getrandbits(64)
            prompt_config = get_and_fill_template(values_map)
            prompt = json.loads(prompt_config)

            if values_map['prompt'] is None:
                del values_map['prompt']
            if values_map['negative_prompt'] is None:
                del values_map['negative_prompt']

        else:
            comfy_ui_command = ComfyUICommand(ctx=interaction.context, **prompt_values)
            ApplicationContext = namedtuple("ApplicationContext", "interaction")
            Interaction = namedtuple("Interaction", "user")
            mock_interaction = Interaction(interaction.user.mention)
            mock_ctx = ApplicationContext(mock_interaction)
            comfy_ui_command.ctx = mock_ctx

            values_map = comfy_ui_command.get_values_map()
            prompt = comfy_ui_command.get_prompt()

        insert_prompt(response_message.id, response_message.channel.id, interaction.user.mention, command_name, values_map)

        # interaction = await MyBotInteraction.create(bot=None, data=comfy_ui_command)

        queue_response = await queue_prompt(prompt)
        prompt_id = queue_response['prompt_id']
        update_prompt_id_for_message_id(response_message.id, prompt_id)
        log.info("done with regenerate action")


    @discord.ui.button(
        style=discord.ButtonStyle.secondary,
        custom_id="image:prompt",
        label="Get Prompt"
    )
    async def print_prompt(self, button, interaction):
        prompt_info = get_prompt_information_for_message_id(interaction.message.id)

        if prompt_info is None:
            msg = "Unable to retrieve prompt information for the image"
        else:
            prompt_values = json.loads(prompt_info.prompt_values)

            if prompt_info.command_name == 'anime' and 'workflow' in prompt_values:
                del prompt_values['workflow']

            msg = f"```\n/{prompt_info.command_name} "
            for key, value in prompt_values.items():
                if value is not None:
                    msg += f"{key}: {value} "
            msg += "\n```"

        await interaction.response.send_message(msg, ephemeral=True)


    @discord.ui.button(
        style=discord.ButtonStyle.danger,
        custom_id="image:delete",
        label="Delete"
    )
    async def delete_message(self, button, interaction):
        delete_prompt_information_for_message_id(interaction.message.id)
        await interaction.message.delete()
