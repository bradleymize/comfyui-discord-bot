from string import Template
from enum import Enum
from typing import Union
import random
import discord
import importlib.resources
import logging
import json

log = logging.getLogger(__name__)
interaction_queue = []

class Reaction(Enum):
    REPEAT = "🔁"
    DELETE = "❌"

class InteractionType(Enum):
    COMFY_UI_COMMAND = 1
    REPEAT = 2
    DELETE = 3

# TODO: Defaults for given workflow (width / height / steps / cfg scale)
class ComfyUICommand():
    def __init__(
            self,
            ctx: discord.ApplicationContext,
            prompt: str,
            workflow: str = "default.json.template",
            seed: str = None,
            width: int = 1024,
            height: int = 1024,
            steps: int = 4,
            cfg: int = 1
    ):
        self.ctx = ctx
        self.prompt = prompt.replace("\"", "\\\"") # Make prompt JSON friendly
        self.workflow = workflow

        if seed is None:
            self.seed = random.getrandbits(64)
        else:
            self.seed = int(seed) #TODO: Error handling

        self.width = width
        self.height = height
        self.steps = steps
        self.cfg = cfg

    def get_values_map(self) -> dict:
        return {
            'workflow': self.workflow,
            'seed': self.seed,
            'width': self.width,
            'height': self.height,
            'steps': self.steps,
            'cfg': self.cfg,
            'prompt': self.prompt
        }

class MyBotInteraction():
    interaction_type: InteractionType
    mention: Union[None, discord.User, discord.Member] = None
    message: Union[None, discord.Message] = None
    reply_to: Union[None, discord.Message] = None
    data: Union[discord.RawReactionActionEvent, ComfyUICommand]
    values_map: dict
    prompt_id: str = None

    @classmethod
    async def create(
            cls,
            bot: discord.Bot,
            data: Union[discord.RawReactionActionEvent, ComfyUICommand]
    ):
        self = cls()
        self.data = data

        if isinstance(data, discord.RawReactionActionEvent):
            if data.emoji.name == Reaction.REPEAT.value:
                self.interaction_type = InteractionType.REPEAT
            elif data.emoji.name == Reaction.DELETE.value:
                self.interaction_type = InteractionType.DELETE
            else:
                raise Exception(f"Unsupported reaction: {data.emoji.name}")

            #TODO: Add error handling for fetching stuff (e.g. try deleting different bot message, try deleting queue message)
            channel = await bot.fetch_channel(data.channel_id)
            self.message = await channel.fetch_message(data.message_id)
            self.reply_to = await channel.fetch_message(self.message.reference.message_id)
            self.mention = await bot.fetch_user(data.user_id)
            self.values_map = parse_message(self.reply_to.content)

            if self.interaction_type == InteractionType.REPEAT:
                self.values_map['seed'] = random.getrandbits(64)
        elif isinstance(data, ComfyUICommand):
            self.interaction_type = InteractionType.COMFY_UI_COMMAND
            self.mention = data.ctx.interaction.user
            self.values_map = data.get_values_map()
        else:
            raise Exception(f"Unsupported interaction data: {type(data).__name__}")

        return self

    def get_prompt(self):
        log.info("Getting workflow template and prompt")
        prompt_config = get_and_fill_template(self.values_map)
        prompt = json.loads(prompt_config)
        return prompt

    def __repr__(self):
        return f"MyBotInteraction({self.interaction_type.name}, mention {self.mention} when replying to message {self.reply_to.id})\n{self.values_map}"

def is_valid_reaction(payload: discord.RawReactionActionEvent, bot_id: int) -> bool:
    emoji_name = payload.emoji.name
    is_bot = payload.member.bot
    # Must be a supported emoji
    # Must not be added by a bot
    # Message it was added to must be created by THIS bot
    return emoji_name in Reaction and not is_bot and payload.data['message_author_id'] == str(bot_id)

def parse_message(msg: str) -> Union[dict, None]:
    lines = msg.splitlines()

    if lines.pop(0).startswith("Queued an image"):
        workflow = lines.pop(0).split(': ')[1]
        seed = lines.pop(0).split(': ')[1]
        width = lines.pop(0).split(': ')[1]
        height = lines.pop(0).split(': ')[1]
        steps = lines.pop(0).split(': ')[1]
        prompt = lines.pop(0).split(': ')[1]

        while not lines[0].startswith("prompt id:"):
            prompt = "\n".join((prompt, lines.pop(0)))

        prompt_id = lines.pop(0) # Unused, prompt_id will be populated

        return {
            'workflow': workflow,
            'seed': seed,
            'width': width,
            'height': height,
            'steps': steps,
            'cfg': 1,
            'prompt': prompt
        }
    else:
        log.warning("Message is not parseable")
        return None

def get_and_fill_template(values_map: dict) -> str:
    log.info(f"Getting workflow: {values_map['workflow']}")
    workflow_template_text = importlib.resources.read_text("src.workflows", values_map['workflow'])
    tpl = Template(workflow_template_text)
    prompt_config = tpl.substitute(**values_map)
    return prompt_config

def get_interaction_by_prompt_id(prompt_id: str) -> MyBotInteraction:
    interaction_list = [interaction for interaction in interaction_queue if interaction.prompt_id == prompt_id]
    if len(interaction_list) == 1:
        return interaction_list[0]
    elif len(interaction_list) > 1:
        log.warning("Multiple interactions found, returning the first one, but this shouldn't happen")
        return interaction_list[0]
    else:
        raise Exception(f"Unable to find interaction with prompt_id: {prompt_id}")

def remove_interaction(interaction: MyBotInteraction):
    log.info("Removing interaction from queue")
    try:
        interaction_queue.remove(interaction)
    except ValueError:
        log.warning("Nothing to remove, interaction is not in the queue")