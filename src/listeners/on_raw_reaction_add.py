import logging

import discord
from src.interface.MyListener import MyListener
from src.botutils import is_valid_reaction

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
        if is_valid_reaction(payload, self.bot.user.id):
            log.info(f"Processing reaction: {payload.emoji.name}")
        else:
            log.info(f"{payload.emoji.name} is not a supported reaction or added by bot, ignoring")