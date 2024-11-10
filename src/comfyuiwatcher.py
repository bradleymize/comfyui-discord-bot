import logging
import io
import discord
import json
import src.bot as my_bot

log = logging.getLogger(__name__)
# TODO: Error handling
async def listen_for_comfyui_messages(ws):
    log.info("Beginning to listen for websocket messages")
    current_node = ""
    current_node_data = None

    while True:
        out = await ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                print(f"Data: {data}")
                if 'prompt_id' in data:
                    if data['node'] is None:
                        continue
                    else:
                        current_node = data['node']
                        current_node_data = data
        else:
            if current_node == 'save_image_websocket_node':
                prompt_id = current_node_data['prompt_id']
                log.info(f"Done processing prompt id: {prompt_id}")
                await send_images(prompt_id, out[8:])
                current_node = ""
                current_node_data = None


async def send_images(prompt_id, image_bytes):
    msg = my_bot.get_message_by_prompt_id(prompt_id)
    msg['image_buffer_list'] = []

    log.info("converting image to buffer")
    b = io.BytesIO(image_bytes)  # Discord requires io.BufferedIOBase, BytesIO inherits from BufferedIOBase
    msg['image_buffer_list'].append(discord.File(b, 'image.png'))

    await msg['response'].reply(f"{msg['user'].mention}", files=msg['image_buffer_list'])
    my_bot.delete_message(msg['id'])