import logging
import io
import discord
import json
import websockets
from src.views.ImageResponseView import ImageResponseView
from src.database import get_information_prompt_id

log = logging.getLogger(__name__)
# TODO: Error handling

bot = None

async def listen_for_comfyui_messages(ws):
    log.info("Beginning to listen for websocket messages")
    current_node = ""
    current_node_data = None

    # TODO: message['type'] == 'execution_success'
    # TODO: somehow get the generated prompt when using wildcards
    images = []
    while True:
        try:
            out = await ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    # print(f"Data: {data}")
                    if 'prompt_id' in data:
                        if data['node'] is None:
                            continue
                        else:
                            current_node = data['node']
                            current_node_data = data
                if message['type'] == 'progress':
                    data = message['data']
                    if 'node' in data:
                        if data['node'] == 'save_image_websocket_node':
                            current_node = data['node']
                            current_node_data = data
            else:
                if current_node == 'save_image_websocket_node':
                    # TODO: handle prompt_id better (never get end for previous message, send what we got, start new message)
                    prompt_id = current_node_data['prompt_id']
                    images.append(out[8:])
                    if len(images) == current_node_data['max']:
                        log.info(f"Done processing prompt id: {prompt_id}")
                        await respond_with_image(prompt_id, images)
                        current_node = ""
                        current_node_data = None
                        images = []
        except websockets.exceptions.ConnectionClosedError as e:
            pass


async def respond_with_image(prompt_id, image_array):
    if bot is None:
        log.error(f"Cannot fetch message to respond to, bot instance is null")
        return

    prompt_info = get_information_prompt_id(prompt_id)
    log.info(f"prompt_info: {prompt_info}")

    log.info("Fetching channel")
    channel = await bot.fetch_channel(prompt_info.channel_id)
    log.info("Fetching message")
    message = await channel.fetch_message(prompt_info.discord_message_id)

    images = []
    for i, image_bytes in enumerate(image_array):
        b = io.BytesIO(image_bytes)  # Discord requires io.BufferedIOBase, BytesIO inherits from BufferedIOBase
        images.append(discord.File(b, f'image-{i+1}.png'))

    log.info(f"Editing message {message.id} with image + view")
    try:
        await message.edit(content=f"{prompt_info.mention_user}", files=images, view=ImageResponseView())
    except Exception as e:
        log.error(str(e))
        await message.edit(content="An error occurred sending the image")
