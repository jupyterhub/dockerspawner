# Build as jupyterhub/singleuser
# Run with the DockerSpawner in JupyterHub

FROM jupyter/base-notebook:b4dd11e16ae4
MAINTAINER Project Jupyter <jupyter@googlegroups.com>

ADD install_jupyterhub /tmp/install_jupyterhub
ARG JUPYTERHUB_VERSION=master
RUN python /tmp/install_jupyterhub
