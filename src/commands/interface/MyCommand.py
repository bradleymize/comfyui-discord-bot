from abc import ABC, abstractmethod
import discord

class MyCommand(ABC):
    @abstractmethod
    def init(self):
        pass