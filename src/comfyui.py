import discord
from string import Template
import websocket
import uuid
import json
import urllib.request
import urllib.parse
import io

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

class ComfyUI:
    async def generate(
            self,
            ctx: discord.ApplicationContext,
            workflow: str,
            values_map: dict
    ) -> list[discord.File]:
        print("getting template")
        tpl = self.get_workflow_template(workflow)
        prompt_config = tpl.substitute(**values_map)

        prompt = json.loads(prompt_config)
        print("connecting to websocket")
        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
        print("getting images")
        images = self.get_images(ws, prompt)
        ws.close() # for in case this example is used in an environment where it will be repeatedly called, like in a Gradio app. otherwise, you'll randomly receive connection timeouts

        image_buffer_list = []

        for node_id in images:
            for image_data in images[node_id]:
                print("converting image to buffer")
                b = io.BytesIO(image_data)  # Discord requires io.BufferedIOBase, BytesIO inherits from BufferedIOBase
                image_buffer_list.append(discord.File(b, 'image.png'))
                # print(f"image_data type = {type(image_data)}")
                # print(f"b type = {type(b)}")
                #
                # with open("image.png", "wb") as binary_file:
                #     binary_file.write(image_data)
        print("returning list of image buffers")
        return image_buffer_list

# ====================================================================================

    def get_workflow_template(self, workflow) -> Template:
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

    def queue_prompt(self,prompt):
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        print("queueing prompt")
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())


    def get_images(self, ws, prompt):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_images = {}
        current_node = ""
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['prompt_id'] == prompt_id:
                        if data['node'] is None:
                            break #Execution is done
                        else:
                            current_node = data['node']
            else:
                if current_node == 'save_image_websocket_node':
                    images_output = output_images.get(current_node, [])
                    images_output.append(out[8:])
                    output_images[current_node] = images_output
        print("generated images")
        return output_images