"""Module for interacting with a comfyui server
"""

import json
import logging
import aiohttp
import uuid

from src.botutils import MyBotInteraction

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())
log = logging.getLogger(__name__)


async def queue_new_prompt(interaction: MyBotInteraction):
    log.info("Queueing prompt")
    prompt = interaction.get_prompt()
    queue_response = await queue_prompt(prompt)
    interaction.prompt_id = queue_response['prompt_id']
    log.info(f"Got prompt id: {interaction.prompt_id}")

async def queue_prompt(prompt):
    async with aiohttp.ClientSession() as session:
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        async with session.post("http://{}/prompt".format(server_address), data=data) as r:
            log.info(f"Post response status: {r.status}")
            if r.status == 200:
                return await r.json()

# TODO: Error handling
async def get_queue_information() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get("http://{}/queue".format(server_address)) as r:
            if r.status == 200:
                js = await r.json()
                is_running = "no"
                if len(js['queue_running']) > 0:
                    is_running = "yes"
                return f"Current queue size: {len(js['queue_pending'])}. Currently generating an image: {is_running}"