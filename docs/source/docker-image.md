# Picking or building a Docker image

By default, DockerSpawner uses the `quay.io/jupyterhub/singleuser` image
with the appropriate tag that pins the right version of JupyterHub,
but you can also build your own image.

## How to pick a Docker image

Any of the existing Jupyter [docker stacks](https://github.com/jupyter/docker-stacks)
can be used with JupyterHub, provided that the version of JupyterHub in the image matches,
and are encouraged as the image of choice. Make sure to pick a tag!

Example:

```python
c.DockerSpawner.image = 'quay.io/jupyter/scipy-notebook:2023-10-23'
```

The docker-stacks are moving targets with always changing versions.
Since you need to make sure that JupyterHub in the image is compatible with JupyterHub,
always include the `:hash` tag part when specifying the image.

## How to build your own Docker image

You can also build your own image.
The only requirements for an image to be used with JupyterHub:

1. it has Python >= 3.6
2. it has JupyterHub version matching your Hub deployment
3. it has the Jupyter `notebook` package
4. CMD launches jupyterhub-singleuser, OR jupyter-labhub, OR the `c.Spawner.cmd` configuration is used
   to do this.

For just about any starting image, you can make it work with JupyterHub by installing
the appropriate JupyterHub version and the Jupyter notebook package.

For instance, from the docker-stacks, pin your JupyterHub version and you are done:

```Dockerfile
FROM quay.io/jupyter/scipy-notebook:67b8fb91f950
ARG JUPYTERHUB_VERSION=4.0.2
RUN pip3 install --no-cache \
    jupyterhub==$JUPYTERHUB_VERSION
```

Or for the absolute minimal JupyterHub user image starting only from the base Python image:

**NOTE: make sure to pick the jupyterhub version you are using!**

```Dockerfile
FROM python:3.11
RUN pip3 install \
    'jupyterhub==4.*' \
    'notebook==7.*'

# create a user, since we don't want to run as root
RUN useradd -m jovyan
ENV HOME=/home/jovyan
WORKDIR $HOME
USER jovyan

CMD ["jupyterhub-singleuser"]
```

This Dockerfile should work with just about any base image in the `FROM` line,
provided it has Python 3 installed.
