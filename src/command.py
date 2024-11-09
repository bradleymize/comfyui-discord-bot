import discord
import random

from src.comfyui import ComfyUI


class Command:
    def initialize(self, bot):

        print("Initializing comfyui command")

        @bot.command(description="Creates an AI image using ComfyUI") # this decorator makes a slash command
        # @discord.option("workflow", type=discord.SlashCommandOptionType.string, required=True)
        @discord.option("prompt", type=discord.SlashCommandOptionType.string, required=True)
        @discord.option("seed", type=discord.SlashCommandOptionType.integer, required=False)
        @discord.option("width", type=discord.SlashCommandOptionType.integer, required=False)
        @discord.option("height", type=discord.SlashCommandOptionType.integer, required=False)
        @discord.option("steps", type=discord.SlashCommandOptionType.integer, required=False)
        async def comfyui(
                ctx: discord.ApplicationContext,
                # workflow: str,
                prompt: str,
                seed: int,
                width: int,
                height: int,
                steps: int
        ): # a slash command will be created with the name "ping"
            if seed is None:
                seed = random.getrandbits(64)
            if width is None:
                width = 1024
            if height is None:
                height = 1024
            if steps is None:
                steps = 4

            values_map = {
                'seed': seed,
                'width': width,
                'height': height,
                'steps': steps,
                'cfg': 1,
                'prompt': prompt
            }

            msg = f"""Created image using the following config:
seed: {seed}
width: {width}
height: {height}
steps: {steps}
prompt: {prompt}"""

            comfyui = ComfyUI()
            print("Calling comfyui.generate")
            await ctx.defer()
            image_buffer_list = await comfyui.generate(ctx, None, values_map)
            print("sending image buffer response")
            await ctx.followup.send(f"{msg}", files=image_buffer_list)