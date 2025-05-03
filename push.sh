#!/usr/bin/env bash

if [[ "${1}" == "dev" ]]; then
  timestamp="$(cat versionDev)"
  echo "Pushing dev image (timestamp only)"
else
  timestamp="$(cat version)"
  echo "Pushing prod images (latest + timestamp)"
  docker push "registry.b-rad.dev:443/comfyui-discord-bot:latest"
fi

docker push "registry.b-rad.dev:443/comfyui-discord-bot:${timestamp}"