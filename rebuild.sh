#!/bin/bash

docker compose -f docker-compose.dev.yaml down; docker rmi comfyui-discord-bot-prod:0.12.0-SNAPSHOT; docker compose -f docker-compose.dev.yaml up
