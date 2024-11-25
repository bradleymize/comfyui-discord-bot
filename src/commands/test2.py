from src.commands.interface.MyCommand import MyCommand
import discord

class TestTwo(MyCommand):
    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        self.cmd_meta = {
            'name': 'test2',
            'description': 'A complex but basic command'
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
                'description': "Number used to help re-create images. Default: (random)"
            },
            {
                'name': 'width',
                'type': discord.SlashCommandOptionType.integer,
                'required': False,
                'description': "The desired width of the generated image. Default: 1024"
            },
            {
                'name': 'height',
                'type': discord.SlashCommandOptionType.integer,
                'required': False,
                'description': "The desired height of the generated image. Default: 1024"
            },
            {
                'name': 'steps',
                'type': discord.SlashCommandOptionType.integer,
                'required': False,
                'description': "The number of iterations to perform when generating the image. Default: 4"
            }
        ]
        self.fn = self.command
        super().register_command()

    def get_workflows(
            self,
            ctx: discord.commands.context.AutocompleteContext
    ):
        return ["foo", "bar"]

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
        msg = f"""Received arguments:
workflow: {workflow}
seed: {seed}
width: {width}
height: {height}
steps: {steps}
prompt: {prompt}
"""
        await ctx.respond(msg)