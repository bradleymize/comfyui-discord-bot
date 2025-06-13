import discord
import json
import math
from src.commands.experiment import log


class LoraResponseView(discord.ui.View):
    MAX_PER_PAGE = 25

    def __init__(self):
        super().__init__(timeout=None)


    def get_page(self, page):
        start_index = page * self.MAX_PER_PAGE
        end_index = start_index + self.MAX_PER_PAGE

        loras = []
        with open('src/models/lora.json') as f:
            loras = json.load(f)

        message = f"Page {page + 1} / {math.ceil(len(loras) / self.MAX_PER_PAGE)}\n"
        for i, lora in enumerate(loras[start_index:end_index], start=start_index):
            message += f"{i + 1}. {lora['modelName']}\n"

        return message


    @discord.ui.button(
        style=discord.ButtonStyle.primary,
        custom_id="lora:previous",
        emoji="⬅️",
        label="Previous"
    )
    async def previous_batch(self, button, interaction):
        log.info("Get previous batch of loras")
        content = interaction.message.content
        first_line = content.splitlines()[0]
        current_page = int(first_line.split()[1])
        max_pages = int(first_line.split()[3])

        next_page = current_page - 2 # since 0 based, if current page is 2, then page 1 would start at 0 * max_per_page
        if current_page == 1:
            next_page = max_pages - 1

        message = self.get_page(next_page)

        await interaction.response.edit_message(content=message, view=LoraResponseView())


    @discord.ui.button(
        style=discord.ButtonStyle.primary,
        custom_id="image:next",
        emoji="➡️",
        label="Next"
    )
    async def next_batch(self, button, interaction):
        log.info("Get next batch of loras")
        content = interaction.message.content
        first_line = content.splitlines()[0]
        current_page = int(first_line.split()[1])
        max_pages = int(first_line.split()[3])

        next_page = current_page # since 0 based, if current page is 1, then page 2 would start at 1 * max_per_page
        if current_page == max_pages:
            next_page = 0

        message = self.get_page(next_page)

        await interaction.response.edit_message(content=message, view=LoraResponseView())
