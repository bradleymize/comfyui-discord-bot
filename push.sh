#!/usr/bin/env bash

timestamp="$(cat version)"

echo "${timestamp}" > version

docker push "registry.b-rad.dev:443/comfyui-discord-bot:latest"
docker push "registry.b-rad.dev:443/comfyui-discord-bot:${timestamp}"