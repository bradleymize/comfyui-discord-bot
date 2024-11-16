from typing import Union

import discord
import logging

log = logging.getLogger(__name__)
message_queue = []

def process_request(ctx: discord.ApplicationContext):
    # log.info("Processing request")
    # log.info("-----------------------------------------")
    # # attrs = vars(ctx.interaction)
    # # log.info('\n'.join("%s: %s" % item for item in attrs.items()))
    # log.info(f"ID: {ctx.interaction.id}")
    # log.info(f"User: {ctx.interaction.user}")
    # log.info(f"Channel: {ctx.interaction.channel}")
    # log.info(f"Token: {ctx.interaction.token}")
    # # await ctx.interaction.respond()
    # log.info("-----------------------------------------")
    req = {
        'id': ctx.interaction.id,
        'user': ctx.interaction.user,
        'channel': ctx.interaction.channel,
        'interaction': ctx.interaction
    }
    message_queue.append(req)
    return req

def get_message(id:str):
    msg_list = [msg for msg in message_queue if msg['id'] == id]
    if len(msg_list) > 0:
        return msg_list[0]
    else:
        log.error(f"Unable to find message with id: {id}")
        return {}

def get_message_by_prompt_id(id:str):
    msg_list = [msg for msg in message_queue if msg['prompt_id'] == id]
    if len(msg_list) > 0:
        return msg_list[0]
    else:
        log.error(f"Unable to find message with id: {id}")
        return None

def delete_message(id:str):
    msg = get_message(id)
    if 'id' in msg:
        message_queue.remove(msg)
    else:
        log.warning(f"Unable to delete message with id: {id} - Not Found")

