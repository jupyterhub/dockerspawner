FROM jupyterhub
RUN pip install jupyterhub-dummyauthenticator
RUN npm i -g https://github.com/jupyterhub/configurable-http-proxy/archive/master.tar.gz
COPY setup.py /src/dockerspawner/setup.py
COPY requirements.txt /src/dockerspawner/requirements.txt
RUN pip install -r /src/dockerspawner/requirements.txt
COPY dockerspawner /src/dockerspawner/dockerspawner
RUN pip install /src/dockerspawner
COPY examples/internal-ssl/jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py
