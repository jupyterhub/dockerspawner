# base image: jupyterhub
# this is built by docker-compose
# from the root of this repo
ARG JUPYTERHUB_VERSION=1.3.0
FROM jupyterhub/jupyterhub:${JUPYTERHUB_VERSION}
# install dockerspawner from the current repo
ADD . /tmp/dockerspawner
RUN pip install --no-cache /tmp/dockerspawner
# load example configuration
ADD examples/swarm/jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
