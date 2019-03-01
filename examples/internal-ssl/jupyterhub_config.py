import os
c = get_config() # noqa
c.JupyterHub.authenticator_class = 'dummy'

from dockerspawner import DockerSpawner
c.JupyterHub.spawner_class = DockerSpawner

c.ConfigurableHTTPProxy.should_start = False
c.ConfigurableHTTPProxy.api_url = 'https://proxy:8001'

c.JupyterHub.internal_ssl = True

c.DockerSpawner.image = os.environ['DOCKER_NOTEBOOK_IMAGE']
c.DockerSpawner.remove_containers = True
c.JupyterHub.log_level = 10

c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_connect_ip = 'jupyterhub'
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
c.JupyterHub.internal_certs_location = os.environ['INTERNAL_SSL_PATH']
# c.JupyterHub.recreate_internal_certs = True
c.JupyterHub.trusted_alt_names = ["DNS:jupyterhub", "DNS:proxy"]
