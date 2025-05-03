from src.interface.MyCommand import MyCommand
import logging
import discord
import json
import os

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


    # TODO: Derive this from the comfyui volume mount
    def get_models(self, ctx: discord.commands.context.AutocompleteContext):
        # Construct from: https://embed.dan.onl/
        models = [
            discord.OptionChoice("Boleromix(Pony) v2.10", "boleromixPony_v210.safetensors.json"),
            discord.OptionChoice("DreamShaper XL Turbo v2.1", "dreamshaperXL_v21TurboDPMSDE.safetensors.json"),
            discord.OptionChoice("PixelWave FLUX Schnell v3", "pixelwave_flux1Schnell03.safetensors.json"),
            discord.OptionChoice("Pony Diffusion XL v6", "ponyDiffusionV6XL_v6StartWithThisOne.safetensors.json"),
            discord.OptionChoice("ReV Animated Rebirth v2", "revAnimated_v2Rebirth.safetensors.json")
        ]
        return models


    async def command(
            self,
            ctx: discord.ApplicationContext,
            model: str
    ):
        log.info(f"Getting information about {model}")
        embeds = []
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

        log.info("Sending response")
        await ctx.send_response(embeds=embeds, ephemeral=True)
