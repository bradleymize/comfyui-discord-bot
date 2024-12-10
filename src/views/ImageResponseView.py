import json
from collections import namedtuple
import discord

from src.botutils import ComfyUICommand, MyBotInteraction
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

        comfy_ui_command = ComfyUICommand(ctx=interaction.context, **prompt_values)
        ApplicationContext = namedtuple("ApplicationContext", "interaction")
        Interaction = namedtuple("Interaction", "user")
        mock_interaction = Interaction(interaction.user.mention)
        mock_ctx = ApplicationContext(mock_interaction)
        comfy_ui_command.ctx = mock_ctx

        values_map = comfy_ui_command.get_values_map()
        insert_prompt(response_message.id, response_message.channel.id, interaction.user.mention, command_name, values_map)

        interaction = await MyBotInteraction.create(bot=None, data=comfy_ui_command)

        queue_response = await queue_prompt(interaction.get_prompt())
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
            msg = f"```\n/{prompt_info.command_name} "
            for key, value in prompt_values.items():
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
