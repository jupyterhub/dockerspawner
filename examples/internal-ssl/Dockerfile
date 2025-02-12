FROM jupyterhub/jupyterhub:5

COPY pyproject.toml setup.py requirements.txt /src/dockerspawner/
COPY dockerspawner /src/dockerspawner/dockerspawner
RUN pip install /src/dockerspawner

COPY examples/internal-ssl/jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
