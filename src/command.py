import discord
import logging
import src.comfyutils as my_comfyui
from src.botutils import MyBotInteraction, is_valid_reaction, Reaction
from src.commandloader import load_commands

log = logging.getLogger(__name__)

class Command:
    def initialize(self, bot, websocket):

        load_commands("src.commands", bot)


        @bot.listen
        async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
            log.info(f"Processing reaction: {payload.emoji.name}")

            if is_valid_reaction(payload, bot.user.id):

                if payload.emoji.name == Reaction.REPEAT.value:
                    # emoji is a supported reaction
                    interaction = await MyBotInteraction.create(bot=bot, data=payload)
                    if isinstance(interaction.values_map, dict):
                        log.info("queueing prompt stuff")
                        await my_comfyui.queue_new_prompt(interaction)
                        status = await my_comfyui.get_queue_information()
                        await interaction.reply_to.channel.send(f"{interaction.mention.mention}, regenerating the image with a new seed... {status}")
                    else:
                        log.warning("Message is not one that can regenerate stuff")
                elif payload.emoji.name == Reaction.DELETE.value:
                    interaction = await MyBotInteraction.create(bot=bot, data=payload)
                    await interaction.message.delete()
            else:
                log.info(f"{payload.emoji.name} is not a supported reaction or added by bot, ignoring")