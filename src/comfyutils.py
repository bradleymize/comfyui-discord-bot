"""Module for interacting with a comfyui server
"""

import json
import logging
import aiohttp
import uuid
import discord
from typing import List
import os

# API documentation: https://github.com/comfyanonymous/ComfyUI/blob/master/server.py

server_address = os.getenv('COMFYUI_ADDRESS') #"127.0.0.1:8188"
client_id = str(uuid.uuid4())
log = logging.getLogger(__name__)


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

# TODO: Consider hard-coding samplers for faster response, with potential toggle flag (in code) to dynamically get
async def get_sampler_names(*args, **kwargs) -> List[str]:
    async with aiohttp.ClientSession() as session:
        async with session.get("http://{}/object_info/KSampler".format(server_address)) as r:
            if r.status == 200:
                js = await r.json()
                return js['KSampler']['input']['required']['sampler_name'][0]

# TODO: Consider hard-coding schedulers for faster response, with potential toggle flag (in code) to dynamically get
async def get_schedulers(*args, **kwargs) -> List[str]:
    async with aiohttp.ClientSession() as session:
        async with session.get("http://{}/object_info/KSampler".format(server_address)) as r:
            if r.status == 200:
                js = await r.json()
                return js['KSampler']['input']['required']['scheduler'][0]

async def post_image(name: str, attachment: discord.Attachment):
    async with aiohttp.ClientSession() as session:
        file = await attachment.to_file()
        data = aiohttp.FormData()
        data.add_field('image', file.fp, filename=name, content_type=attachment.content_type)
        async with session.post("http://{}/upload/image".format(server_address), data=data) as r:
            if r.status != 200:
                raise Exception("Error uploading image")