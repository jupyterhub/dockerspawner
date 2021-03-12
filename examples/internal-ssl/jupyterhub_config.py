import os
import socket
import sys
import time


c = get_config()  # noqa
c.JupyterHub.authenticator_class = 'dummy'

c.JupyterHub.spawner_class = 'docker'

# wait for proxy DNS to resolve
# hub startup will crash if it doesn't
for i in range(30):
    try:
        socket.gethostbyname("proxy")
    except socket.gaierror as e:
        socket_error = e
        print(f"Waiting for proxy: {e}", file=sys.stderr)
        time.sleep(1)
    else:
        break
else:
    raise socket_error

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
