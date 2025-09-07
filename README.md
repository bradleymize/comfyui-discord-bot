# Development Setup
Run the following to spin up a development environment
```bash
./startDev.sh
```

# Running the dev bot
Within the development environment created above, run
```bash
python run.py
```
Scaling down the deployment
```bash
kubectl -n comfyui-discord-bot scale deployment comfyui-discord-bot-dev --replicas 0
```

# Tests
Within the development environment created above, run
```bash
pytest --cov --cov-report=html:coverage
```

# Adding New Models
* Create a model info "card" in `src/models/info` with the same name as the model (with the `.md` extension added)
* Create the defaults for the model in `src/models/defaults`
* Add the model to the supported workflow(s) in `src/models`

# Releasing a new version
* Merge branch into main
* Make sure `docker-compose.prod.yaml` version has been updated for image + environment variable
* Run `docker compse -f docker-compose.prod.yaml up`

# Building new image for helmfile use
* Run `./buildMultiArch.sh` (for dev images, run `./buildMultiArch.sh dev`)
* Run `./push.sh` (for dev images, run `./push.sh dev`)
* Update the image tag in the respective `helmfile.d/file.yaml` file
* Apply the helmfile (optionally with the name of the specific release to apply)