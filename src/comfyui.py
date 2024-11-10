import discord
from string import Template
import json
import urllib.request
import urllib.parse
import io
import logging
import aiohttp
import uuid

import src.bot as my_bot

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())
log = logging.getLogger(__name__)


async def generate(
        ctx: discord.ApplicationContext,
        websocket,
        workflow: str,
        values_map: dict
):

    log.info("getting template")
    tpl = get_workflow_template(workflow)
    prompt_config = tpl.substitute(**values_map)
    prompt = json.loads(prompt_config)

    log.info("Queueing prompt")
    queue_response = await queue_prompt_2(prompt)
    prompt_id = queue_response['prompt_id']
    log.info(f"Got prompt id: {prompt_id}")
    my_bot.get_message(ctx.interaction.id)['prompt_id'] = prompt_id

    return prompt_id

    # log.info("getting images")
    # images = await get_images_2(websocket, prompt_id)
    #
    # image_buffer_list = []
    #
    # for node_id in images:
    #     for image_data in images[node_id]:
    #         log.info("converting image to buffer")
    #         b = io.BytesIO(image_data)  # Discord requires io.BufferedIOBase, BytesIO inherits from BufferedIOBase
    #         image_buffer_list.append(discord.File(b, 'image.png'))
    # log.info("returning list of image buffers")
    # return image_buffer_list

# ====================================================================================

def get_workflow_template(workflow) -> Template:
    return Template("""
{
"3": {
"inputs": {
  "seed": ${seed},
  "steps": ${steps},
  "cfg": ${cfg},
  "sampler_name": "dpmpp_2m",
  "scheduler": "sgm_uniform",
  "denoise": 1,
  "model": [
    "10",
    0
  ],
  "positive": [
    "6",
    0
  ],
  "negative": [
    "7",
    0
  ],
  "latent_image": [
    "5",
    0
  ]
},
"class_type": "KSampler",
"_meta": {
  "title": "KSampler"
}
},
"5": {
"inputs": {
  "width": ${width},
  "height": ${height},
  "batch_size": 1
},
"class_type": "EmptyLatentImage",
"_meta": {
  "title": "Empty Latent Image"
}
},
"6": {
"inputs": {
  "text": "${prompt}",
  "clip": [
    "11",
    0
  ]
},
"class_type": "CLIPTextEncode",
"_meta": {
  "title": "CLIP Text Encode (Prompt)"
}
},
"7": {
"inputs": {
  "text": "",
  "clip": [
    "11",
    0
  ]
},
"class_type": "CLIPTextEncode",
"_meta": {
  "title": "CLIP Text Encode (Prompt)"
}
},
"8": {
"inputs": {
  "samples": [
    "3",
    0
  ],
  "vae": [
    "12",
    0
  ]
},
"class_type": "VAEDecode",
"_meta": {
  "title": "VAE Decode"
}
},
"10": {
"inputs": {
  "unet_name": "pixelwave_flux1Schnell03.safetensors",
  "weight_dtype": "fp8_e4m3fn"
},
"class_type": "UNETLoader",
"_meta": {
  "title": "Load Diffusion Model"
}
},
"11": {
"inputs": {
  "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
  "clip_name2": "clip_l.safetensors",
  "type": "flux"
},
"class_type": "DualCLIPLoader",
"_meta": {
  "title": "DualCLIPLoader"
}
},
"12": {
"inputs": {
  "vae_name": "ae.safetensors"
},
"class_type": "VAELoader",
"_meta": {
  "title": "Load VAE"
}
},
"save_image_websocket_node": {
"class_type": "SaveImageWebsocket",
"inputs": {
  "images": [
    "8",
    0
  ]
}
}
}
""")

# def queue_prompt(prompt):
#     p = {"prompt": prompt, "client_id": client_id}
#     data = json.dumps(p).encode('utf-8')
#     log.info("queueing prompt")
#     req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
#     return json.loads(urllib.request.urlopen(req).read())

# def get_images(ctx:discord.ApplicationContext, ws, prompt):
#     prompt_id = queue_prompt(prompt)['prompt_id']
#     req = my_bot.get_message(ctx.interaction.id)
#     req['prompt_id'] = prompt_id
#     log.info(f"Got prompt id: {prompt_id}")
#     output_images = {}
#     current_node = ""
#     while True:
#         out = ws.recv()
#         if isinstance(out, str):
#             message = json.loads(out)
#             if message['type'] == 'executing':
#                 data = message['data']
#                 if data['prompt_id'] == prompt_id:
#                     if data['node'] is None:
#                         break #Execution is done
#                     else:
#                         current_node = data['node']
#         else:
#             if current_node == 'save_image_websocket_node':
#                 images_output = output_images.get(current_node, [])
#                 images_output.append(out[8:])
#                 output_images[current_node] = images_output
#     log.info("generated images")
#     return output_images

# ====================================================================================

async def queue_prompt_2(prompt):
    async with aiohttp.ClientSession() as session:
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        async with session.post("http://{}/prompt".format(server_address), data=data) as r:
            log.info(f"Post response status: {r.status}")
            if r.status == 200:
                return await r.json()

# TODO: This is blocking
# async def get_images_2(ws, prompt_id):
#     output_images = {}
#     current_node = ""
#     while True:
#         out = await ws.recv()
#         if isinstance(out, str):
#             message = json.loads(out)
#             if message['type'] == 'executing':
#                 data = message['data']
#                 print(f"Data: {data} - Prompt ID: {prompt_id}")
#                 if 'prompt_id' in data:
#                     if data['node'] is None:
#                         break #Execution is done
#                     else:
#                         current_node = data['node']
#         else:
#             if current_node == 'save_image_websocket_node':
#                 images_output = output_images.get(current_node, [])
#                 images_output.append(out[8:])
#                 output_images[current_node] = images_output
#     log.info("generated images")
#     return output_images

async def get_queue_information() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get("http://{}/queue".format(server_address)) as r:
            if r.status == 200:
                js = await r.json()
                is_running = "no"
                if len(js['queue_running']) > 0:
                    is_running = "yes"
                return f"Current queue size: {len(js['queue_pending'])}. Currently generating an image: {is_running}"