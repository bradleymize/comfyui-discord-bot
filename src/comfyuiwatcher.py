import logging
import io
import discord
import json
from src.views.ImageResponseView import ImageResponseView
from src.database import get_information_prompt_id

log = logging.getLogger(__name__)
# TODO: Error handling

bot = None

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
                # print(f"Data: {data}")
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
                current_node = ""
                current_node_data = None
                await respond_with_image(prompt_id, out[8:])

# async def send_images(prompt_id, image_bytes):
#     # log.info("converting image to buffer")
#     b = io.BytesIO(image_bytes)  # Discord requires io.BufferedIOBase, BytesIO inherits from BufferedIOBase
#
#     images = []
#     images.append(discord.File(b, 'image.png'))
#     # log.info(images)
#
#     # log.info(botutils.interaction_queue)
#
#     # log.info("getting message from interaction")
#     interaction = botutils.get_interaction_by_prompt_id(prompt_id)
#     # log.info(interaction)
#     msg = interaction.reply_to
#
#     log.info("Replying to original message with image")
#     reply_msg = await msg.reply(f"{interaction.mention.mention}, regenerated image with new seed: {interaction.values_map['seed']}", files=images)
#     await reply_msg.add_reaction(botutils.Reaction.REPEAT.value)
#     await reply_msg.add_reaction(botutils.Reaction.DELETE.value)
#     botutils.remove_interaction(interaction)


async def respond_with_image(prompt_id, image_bytes):
    if bot is None:
        log.error(f"Cannot fetch message to respond to, bot instance is null")
        return

    prompt_info = get_information_prompt_id(prompt_id)
    log.info(f"prompt_info: {prompt_info}")

    log.info("Fetching channel")
    channel = await bot.fetch_channel(prompt_info.channel_id)
    log.info("Fetching message")
    message = await channel.fetch_message(prompt_info.discord_message_id)

    b = io.BytesIO(image_bytes)  # Discord requires io.BufferedIOBase, BytesIO inherits from BufferedIOBase
    images = []
    images.append(discord.File(b, 'image.png'))

    embed = discord.Embed(
        color=int("0x3498db", 16),
        image="attachment://image.png"
    )

    log.info(f"Editing message {message.id} with image + view")
    try:
        await message.edit(content=f"{prompt_info.mention_user}", embeds=[embed], files=images, view=ImageResponseView())
    except Exception as e:
        log.error(str(e))
        await message.edit(content="An error occurred sending the image")
