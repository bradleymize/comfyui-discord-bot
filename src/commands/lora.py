import json
import logging
import math
import urllib.parse
import discord
import os

from src.interface.MyCommand import MyCommand
from src.views.LoraResponseView import LoraResponseView

log = logging.getLogger(__name__)

class Lora(MyCommand):
    MAX_PER_PAGE = 25

    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'lora' if os.getenv("BOT_TYPE") == 'PRODUCTION' else 'dev-lora',
            'description': 'Lists all the currently available loras, or if an index is given, returns information on that lora'
        }
        self.options = [
            {
                'name': 'index',
                'type': discord.SlashCommandOptionType.integer,
                'required': False,
                'default': None,
                'min_value': 1,
                'description': "The index of the lora to describe"
            }
        ]
        self.fn = self.command
        super().register_command()


    async def command(
            self,
            ctx: discord.ApplicationContext,
            index: int = None
    ):
        log.info("Running lora command")

        loras = []
        with open('src/models/lora.json') as f:
            loras = json.load(f)

        if index is None:
            message = f"Page 1 / {math.ceil(len(loras) / self.MAX_PER_PAGE)}\n"
            for i, lora in enumerate(loras[:self.MAX_PER_PAGE]):
                message += f"{i + 1}. {lora['modelName']}\n"

            await ctx.send_response(message, view=LoraResponseView(), ephemeral=True)
        elif index < 1:
            message = "'index' must be greater than or equal to 1"
            await ctx.send_response(message, ephemeral=True)
        elif index > len(loras):
            message = f"'index' must be less than or equal to {len(loras)}"
            await ctx.send_response(message, ephemeral=True)
        else:
            lora = loras[index - 1]

            description = f"Trained Words/Phrases:\n"
            description += "\n".join(f"* `{item}`" for item in lora['trainedWords'])

            embed = discord.Embed(
                color=int("0x3498db", 16),
                title=lora['modelName'],
                description=description,
                image=f"https://b-rad.dev/images/ai/lora/{urllib.parse.quote(lora['filenameRoot'])}.webp",
            )
            embed.add_field(name="Usage", value=lora['usage'])
            await ctx.respond(embed=embed, ephemeral=True)

        log.info("done with lora command")
