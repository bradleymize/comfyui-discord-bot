#!/bin/bash

docker run \
  --rm \
  -v .:/app \
  -w /app \
  -u "$(id -u):$(id -g)" \
  --network host \
  -it \
  python:3.13.0 /bin/bash