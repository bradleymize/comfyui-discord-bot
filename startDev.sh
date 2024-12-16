#!/bin/bash

docker run \
  --rm \
  --name discord-bot-dev \
  -v .:/app \
  -w /app \
  -u "$(id -u):$(id -g)" \
  --network host \
  -it \
  python:3.13.0 /bin/bash -c "source venv/bin/activate && pip install -r requirements.txt && /bin/bash"