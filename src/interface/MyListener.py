from abc import ABC, abstractmethod
import discord
import logging

log = logging.getLogger(__name__)

class MyListener(ABC):
    bot = None
    event_name = None

    @abstractmethod
    def init(self):
        pass