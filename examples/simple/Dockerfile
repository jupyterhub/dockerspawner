ARG JUPYTERHUB_VERSION=5
FROM jupyterhub/jupyterhub:$JUPYTERHUB_VERSION
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache -r /tmp/requirements.txt
COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
