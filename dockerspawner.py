"""
A Spawner for JupyterHub that runs each user's server in a separate docker container
"""
import os
from concurrent.futures import ThreadPoolExecutor

import docker
from tornado import gen

from jupyterhub.spawner import Spawner
from IPython.utils.traitlets import Unicode

class DockerSpawner(Spawner):
    
    _executor = None
    @property
    def executor(self):
        """single global executor"""
        cls = self.__class__
        if cls._executor is None:
            cls._executor = ThreadPoolExecutor(1)
        return cls._executor
    
    _client = None
    @property
    def client(self):
        """single global client instance"""
        cls = self.__class__
        if cls._client is None:
            docker_host = os.environ.get('DOCKER_HOST', 'unix://var/run/docker.sock')
            cls._client = docker.Client(base_url=docker_host)
        return cls._client
    
    container_id = Unicode()
    container_ip = Unicode('127.0.0.1', config=True)
    container_image = Unicode("jupyter/singleuser", config=True)
    
    def load_state(self, state):
        super(DockerSpawner, self).load_state(state)
        self.container_id = state.get('container_id', '')
    
    def get_state(self):
        state = super(DockerSpawner, self).get_state()
        state['container_id'] = self.container_id
        return state
    
    def _env_keep_default(self):
        """Don't inherit any env from the parent process"""
        return []
    
    def _env_default(self):
        env = super(DockerSpawner, self)._env_default()
        env.update(dict(
            JPY_USER=self.user.name,
            JPY_COOKIE_NAME=self.user.server.cookie_name,
            JPY_BASE_URL=self.user.server.base_url,
            JPY_HUB_PREFIX=self.hub.server.base_url,
            JPY_HUB_API_URL=self.hub.api_url,
        ))
        return env

    def _docker(self, method, *args, **kwargs):
        """wrapper for calling docker methods
        
        to be passed to ThreadPoolExecutor
        """
        m = getattr(self.client, method)
        return m(*args, **kwargs)
    
    def docker(self, method, *args, **kwargs):
        """Call a docker method in a background thread
        
        returns a Future
        """
        return self.executor.submit(self._docker, method, *args, **kwargs)
    
    @gen.coroutine
    def poll(self):
        """Check for my id in `docker ps`"""
        if not self.container_id:
            raise gen.Return(0)
        
        # if my id is running, return None
        containers = yield self.docker('containers')
        if any(c['Id'] == self.container_id for c in containers):
            raise gen.Return(None)
        
        self.container_id = ''
        raise gen.Return(0)
    
    @gen.coroutine
    def start(self, image=None):
        """start the single-user server in a docker container"""
        if image is None:
            image = self.container_image
        resp = yield self.docker('create_container',
            image=image,
            environment=self.env,
        )
        self.container_id = container_id = resp['Id']
        self.log.info("Created container {}".format(container_id))

        yield self.docker('start', container_id, port_bindings={8888: (self.container_ip,)})
        resp = yield self.docker('port', container_id, 8888)
        self.user.server.port = resp[0]['HostPort']
    
    @gen.coroutine
    def stop(self, now=False):
        """Kill and remove the container
        
        Could pause?
        """
        yield self.docker('kill', self.container_id)
        yield self.docker('remove_container', self.container_id)
        self.container_id = ''
        
