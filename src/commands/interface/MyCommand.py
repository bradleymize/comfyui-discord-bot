from abc import ABC, abstractmethod
import discord
import logging

log = logging.getLogger(__name__)


class MyCommand(ABC):
    bot = None
    cmd_meta = {}
    options = []
    fn = None

    @abstractmethod
    def init(self):
        pass

    def register_command(self):
        log.info(f"Creating command: {self.cmd_meta['name']}")
        for option in list(reversed(self.options)):
            log.info(f"    Registering option: {option['name']}")
            self.fn = discord.option(**option)(self.fn)

        self.bot.command(**self.cmd_meta)(self.fn)
        log.info(f"  Done creating command: {self.cmd_meta['name']}")
