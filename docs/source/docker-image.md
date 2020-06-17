## Picking or building a Docker image

By default, DockerSpawner uses the `jupyterhub/singleuser` image
with the appropriate tag that pins the right version of JupyterHub,
but you can also build your own image.

### How to pick a Docker image
Any of the existing Jupyter [docker stacks](https://github.com/jupyter/docker-stacks)
can be used with JupyterHub, provided that the version of JupyterHub in the image matches,
and are encouraged as the image of choice. Make sure to pick a tag!

Example:
```python
c.DockerSpawner.image = 'jupyter/scipy-notebook:8f56e3c47fec'
```

The docker-stacks are moving targets with always changing versions.
Since you need to make sure that JupyterHub in the image is compatible with JupyterHub,
always include the `:hash` tag part when specifying the image.


### Hot to build your own Docker image
You can also build your own image.
The only requirements for an image to be used with JupyterHub:

1. it has Python >= 3.4
2. it has JupyterHub
3. it has the Jupyter `notebook` package
4. CMD launches jupyterhub-singleuser OR the `c.Spawner.cmd` configuration is used
    to do this.

For just about any starting image, you can make it work with JupyterHub by installing
the appropriate JupyterHub version and the Jupyter notebook package.

For instance, from the docker-stacks, pin your JupyterHub version and you are done:

```Dockerfile
FROM jupyter/scipy-notebook:8f56e3c47fec
ARG JUPYTERHUB_VERSION=0.8.0
RUN pip3 install --no-cache \
    jupyterhub==$JUPYTERHUB_VERSION
```

Or for the absolute minimal JupyterHub user image starting only from the base Python image:

```Dockerfile
FROM python:3.6
RUN pip3 install \
    jupyterhub==0.7.2 \
    'notebook>=5.0,<=6.0'

# create a user, since we don't want to run as root
RUN useradd -m jovyan
ENV HOME=/home/jovyan
WORKDIR $HOME
USER jovyan

CMD ["jupyterhub-singleuser"]
```

This Dockerfile should work with just about any base image in the `FROM` line,
provided it has Python 3 installed.
