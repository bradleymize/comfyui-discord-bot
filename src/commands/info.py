from src.interface.MyCommand import MyCommand
import logging
import discord
import importlib.resources

log = logging.getLogger(__name__)

class ModelInfo(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'model-info',
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
        models = [
            discord.OptionChoice("Boleromix(SDXL) v1.3", "boleromixSDXL_v13.safetensors.md"),
            discord.OptionChoice("DreamShaper XL Turbo v2.1", "dreamshaperXL_v21TurboDPMSDE.safetensors.md"),
            discord.OptionChoice("PixelWave FLUX Schnell v3", "pixelwave_flux1Schnell03.safetensors.md"),
            discord.OptionChoice("Pony Diffusion XL v6", "ponyDiffusionV6XL_v6StartWithThisOne.safetensors.md"),
            discord.OptionChoice("ReV Animated Rebirth v2", "revAnimated_v2Rebirth.safetensors.md")
        ]
        return models


    async def command(
            self,
            ctx: discord.ApplicationContext,
            model: str
    ):
        log.info(f"Getting information about {model}")
        model_info = importlib.resources.read_text("src.models.info", model)
        # TODO: Provide sample images in response
        log.info("Sending response")
        await ctx.send_response(model_info, ephemeral=True)
