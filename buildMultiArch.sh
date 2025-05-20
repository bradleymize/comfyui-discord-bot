#!/usr/bin/env bash

timestamp="$(date "+%Y%m%d-%H%M%S")"

if [[ "${1}" == "dev" ]]; then
  echo "Building dev image"
  echo "${timestamp}" > versionDev
else
  echo "Building prod image"
  echo "${timestamp}" > version
fi

docker buildx build \
  --network host \
  --no-cache \
  --pull \
  --platform linux/amd64,linux/arm64 \
  -t "registry.b-rad.dev:443/comfyui-discord-bot:latest" \
  -t "registry.b-rad.dev:443/comfyui-discord-bot:${timestamp}" \
  .