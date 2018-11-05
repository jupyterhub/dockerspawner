# The proxy is in another container
c.ConfigurableHTTPProxy.should_start = False
c.ConfigurableHTTPProxy.api_url = 'http://proxy:8001'
# tell the hub to use Dummy Auth (for testing)
c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
# use SwarmSpawner
c.JupyterHub.spawner_class = 'dockerspawner.SwarmSpawner'
# The Hub should listen on all interfaces,
# so user servers can connect
c.JupyterHub.hub_ip = '0.0.0.0'
# this is the name of the 'service' in docker-compose.yml
c.JupyterHub.hub_connect_ip = 'hub'
# this is the network name for jupyterhub in docker-compose.yml
# with a leading 'swarm_' that docker-compose adds
c.SwarmSpawner.network_name = 'swarm_jupyterhub-net'

# start jupyterlab
c.Spawner.cmd = ["jupyter", "labhub"]

# debug-logging for testing
import logging
c.JupyterHub.log_level = logging.DEBUG
