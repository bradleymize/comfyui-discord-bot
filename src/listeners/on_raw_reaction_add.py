import logging
from unittest.mock import MagicMock

import discord
from src.interface.MyListener import MyListener
from src.botutils import MyBotInteraction, is_valid_reaction, Reaction, interaction_queue
import src.comfyutils as comfyutils

log = logging.getLogger(__name__)

class OnRawReactionAdd(MyListener):
    event_name = "on_raw_reaction_add"


    def __init__(self, bot: discord.Bot):
        self.bot = bot


    def init(self):
        log.info(f"Initializing {self.event_name} listener")
        @self.bot.listen(self.event_name)
        async def listener(payload: discord.RawReactionActionEvent):
            await self.on_raw_reaction_add(payload)


    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        log.info(f"Processing reaction: {payload.emoji.name}")

        if is_valid_reaction(payload, self.bot.user.id):

            if payload.emoji.name == Reaction.REPEAT.value:
                # emoji is a supported reaction
                interaction = await MyBotInteraction.create(bot=self.bot, data=payload)
                if isinstance(interaction.values_map, dict):
                    interaction_queue.append(interaction)
                    log.info("queueing prompt stuff")
                    await comfyutils.queue_new_prompt(interaction)
                    status = await comfyutils.get_queue_information()
                    await interaction.reply_to.channel.send(f"{interaction.mention.mention}, regenerating the image with a new seed... {status}")
                else:
                    log.warning("Message is not one that can regenerate stuff")
            elif payload.emoji.name == Reaction.DELETE.value:
                interaction = await MyBotInteraction.create(bot=self.bot, data=payload)
                await interaction.message.delete()
        else:
            log.info(f"{payload.emoji.name} is not a supported reaction or added by bot, ignoring")