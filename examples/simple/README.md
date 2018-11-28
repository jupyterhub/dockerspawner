# Running JupyterHub itself in docker

This is a simple example of running jupyterhub in a docker container.

This example will:

- create a docker network
- run jupyterhub in a container
- enable 'dummy authenticator' for testing
- run users in their own containers

It does not:

- enable persistent storage for users or the hub
- run the proxy in its own container

## Initial setup

The first thing we are going to do is create a network for jupyterhub to use.

```bash
docker network create jupyterhub
```

Second, we are going to build our hub image:

```bash
docker build -t hub .
```

We also want to pull the image that will be used:

```bash
docker pull jupyter/base-notebook
```

## Start the hub

To start the hub, we want to:

- run it on the docker network
- expose port 8000
- mount the host docker socket

```bash
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock --net jupyterhub --name jupyterhub -p8000:8000 hub
```

Now we should have jupyterhub running on port 8000 on our docker host.

## Further goals

This shows the *very basics* of running the Hub in a docker container (mainly setting up the network). To run for real, you will want to:

- mount a volume (or a database) for the hub state
- mount volumes for user storage so they don't lose data on each shutdown
- pick a real authenticator
- run the proxy in a separate container so that reloading hub configuration doesn't disrupt users

[jupyterhub-deploy-docker](https://github.com/jupyterhub/jupyterhub-deploy-docker) does all of these things.
