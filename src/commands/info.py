from src.interface.MyCommand import MyCommand
import logging
import discord
import json
import os
from pathlib import Path

log = logging.getLogger(__name__)

class ModelInfo(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'model-info' if os.getenv("BOT_TYPE") == 'PRODUCTION' else 'dev-model-info',
            'description': 'Retrieve basic information about a model'
        }
        self.options = [
            {
                'name': 'model',
                'type': discord.SlashCommandOptionType.string,
                'required': True,
                'description': "The model whose information should be displayed",
                'autocomplete': discord.utils.basic_autocomplete(self.get_models)
            }
        ]
        self.fn = self.command
        super().register_command()


    def get_models(self, ctx: discord.commands.context.AutocompleteContext):
        directory_path = Path(os.getenv('COMFYUI_MODEL_CHECKPOINT_PATH'))
        safetensor_files = sorted(
            f.stem for f in directory_path.glob('*.safetensors') if f.is_file()
        )

        models = [
            discord.OptionChoice(name, f"{name}.safetensors.json")
            for name in safetensor_files
        ]
        return models


    async def command(
            self,
            ctx: discord.ApplicationContext,
            model: str
    ):
        log.info(f"Getting information about {model}")
        embeds = []
        try:
            with open(f'src/models/info/{model}') as f:
                model_embeds_info = json.load(f)

            for embed_info in model_embeds_info:
                fields = None
                if "fields" in embed_info:
                    fields = embed_info['fields']
                    del embed_info['fields']
                if "color" in embed_info:
                    embed_info['color'] = int(embed_info['color'], 16)

                embed = discord.Embed(**embed_info)
                if fields is not None:
                    for field in fields:
                        embed.add_field(**field)
                embeds.append(embed)
        except FileNotFoundError:
            embed = discord.Embed(
                color=int("0x3498db", 16),
                title=f"{model.removesuffix('.safetensors.json')} model information not found",
                description=f"Unable to find the model information for {model.removesuffix('.safetensors.json')} at this time. Sorry"
            )
            embeds.append(embed)

        log.info("Sending response")
        await ctx.send_response(embeds=embeds, ephemeral=True)
