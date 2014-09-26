# DockerSpawner

Enables [JupyterHub](https://github.com/jupyter/jupyterhub) to spawn
user servers in docker containers.

There is a complete example in [examples/oauth](examples/oauth) for
using GitHub OAuth to authenticate users, and spawn containers with docker.

## setup

Install dependencies:

    pip install -r requirements.txt

Tell JupyterHub to use DockerSpawner, by adding the following to your `jupyter_hub_config.py`:

    c.JupyterHubApp.spawner_class='dockerspawner.DockerSpawner'


## build

Build the container with:

    docker build -t jupyter/singleuser singleuser

