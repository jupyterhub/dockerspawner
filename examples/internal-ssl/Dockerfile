FROM jupyterhub/jupyterhub:5

# install dockerspawner from this repo
# alternatively: pip install dockerspawner to get the stable release
COPY ./ dockerspawner /src/dockerspawner
RUN pip install --no-cache /src/dockerspawner

COPY examples/internal-ssl/jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
