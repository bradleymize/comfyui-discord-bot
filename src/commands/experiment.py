from src.interface.MyCommand import MyCommand
import logging
import discord
import json
from src.database import insert_prompt, get_prompt_information_for_message_id, delete_prompt_information_for_message_id, \
    update_prompt_id_for_message_id
import time  # TODO: Remove

log = logging.getLogger(__name__)

class MyView(discord.ui.View):
    def __init__(self, prompt_info):
        super().__init__(timeout=None)
        self.prompt_info = prompt_info


    @discord.ui.button(
        style=discord.ButtonStyle.primary,
        custom_id="image:regenerate",
        emoji="🔁",
        label="Regenerate"
    )
    async def regenerate_callback(self, button, interaction):
        update_prompt_id_for_message_id(interaction.message.id, "random-prompt-id-here")

        await interaction.response.send_message("Working on new generation...")
        response_message = await interaction.original_response()

        new_embed = interaction.message.embeds[0]
        new_embed.image = "https://b-rad.dev/images/ai/revanimated-rebirth-v2/sample-02.png"

        new_prompt_info = {}
        for key,value in self.prompt_info.items():
            new_prompt_info[key] = value
        new_prompt_info['seed'] = 987654321

        interaction_dict = interaction.to_dict()
        command_name = interaction_dict['message']['interaction_metadata']['name']

        insert_prompt(response_message.id, command_name, new_prompt_info)  # TODO: Put this in the command that initially generates the image

        time.sleep(5)  # TODO: Remove artificial wait

        await interaction.edit_original_response(content=f"{interaction.user.mention}", embeds=[new_embed], view=MyView(new_prompt_info))


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

        embed = discord.Embed(
            image="https://b-rad.dev/images/ai/revanimated-rebirth-v2/sample-01.png",
            color=int("0x3498db", 16)
        )
        prompt_info = {
            'prompt': "((best quality)), ((masterpiece)), (detailed), succubus, ethereal beauty, perched on a cloud, (fantasy illustration:1.3), enchanting gaze, leotard, pantyhose, stockings, bodysuit, captivating pose, delicate wings, otherworldly charm, mystical sky, large moon, moonlit night, soft colors, (detailed cloudscape:1.3), (high-resolution:1.2), from below, (rating_explicit), (score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, high res, 4k)",
            'model': "revAnimated_v2Rebirth.safetensors",
            'negative_prompt': "(nude, thighs, cleavage:1.3), 3d, cartoon, anime, sketches, (worst quality, bad quality, child, cropped:1.4) ((monochrome)), ((grayscale)), (rating_safe), (score_3_up, score_4_up, score_5_up, monochrome, vector art, blurry)",
            'width': 512,
            'height': 768,
            'steps': 30,
            'cfg': 8.5,
            'seed': 123456789
        }
        log.info("Sending response")

        interaction = await ctx.send_response(embeds=[embed], view=MyView(prompt_info))
        response_message = await interaction.original_response()
        insert_prompt(response_message.id, self.cmd_meta['name'], prompt_info)
