"""
A Spawner for JupyterHub that runs each user's server in a separate docker container
"""
import itertools
import os
from textwrap import dedent
from concurrent.futures import ThreadPoolExecutor

import docker
from tornado import gen

from jupyterhub.spawner import Spawner
from IPython.utils.traitlets import (
    Bool,
    Dict,
    Unicode,
)

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

    system_users = Bool(
        False,
        config=True,
        help=dedent(
            """
            Users correspond to system users, and as such, their home directory
            will be mounted in the docker container, and the container will be
            run as that user.
            """
        )
    )
    host_homedir_format_string = Unicode(
        "/home/{username}",
        config=True,
        help=dedent(
            """
            Format string for the path to the user's home directory on the host.
            This is only used if `system_users` is set to True. The format
            string should include a `username` variable, which will be formatted
            with the user's username.
            """
        )
    )
    user_ids = Dict(
        config=True,
        help=dedent(
            """
            If system users are being used, then we need to know their user id
            in order to mount the home directory. User ids should be specified
            in this dictionary.
            """
        )
    )

    volumes = Dict(
        config=True,
        help=dedent(
            """
            Map from host file/directory to container file/directory.
            Volumes specified here will be read/write in the container.
            """
        )
    )
    read_only_volumes = Dict(
        config=True,
        help=dedent(
            """
            Map from host file/directory to container file/directory.
            Volumes specified here will be read-only in the container.
            """
        )
    )

    @property
    def host_homedir(self):
        """
        Path to the volume containing the user's home directory on the host. 
        This is only relevant if `self.system_users` is set to True.
        """
        return self.host_homedir_format_string.format(username=self.user.name)

    @property
    def homedir(self):
        """
        Path to the user's home directory in the docker image.
        """
        return "/home/{username}".format(username=self.user.name)

    @property
    def volume_mount_points(self):
        """
        Volumes are declared in docker-py in two stages.  First, you declare
        all the locations where you're going to mount volumes when you call
        create_container.

        Returns a list of all the values in self.volumes or
        self.read_only_volumes.
        """
        mount_points = list(
            itertools.chain(
                self.volumes.values(),
                self.read_only_volumes.values(),
            )
        )

        if self.system_users:
            mount_points.append(self.homedir)

        return mount_points

    @property
    def volume_binds(self):
        """
        The second half of declaring a volume with docker-py happens when you
        actually call start().  The required format is a dict of dicts that
        looks like:

        {
            host_location: {'bind': container_location, 'ro': True}
        }
        """
        volumes = {
            key: {'bind': value, 'ro': False}
            for key, value in self.volumes.items()
        }
        ro_volumes = {
            key: {'bind': value, 'ro': True}
            for key, value in self.read_only_volumes.items()
        }
        volumes.update(ro_volumes)

        if self.system_users:
            volumes[self.host_homedir] = {
                'bind': self.homedir,
                'ro': False
            }

        return volumes

    def load_state(self, state):
        super(DockerSpawner, self).load_state(state)
        self.container_id = state.get('container_id', '')
    
    def get_state(self):
        state = super(DockerSpawner, self).get_state()
        if self.container_id:
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

        if self.system_users:
            env.update(dict(
                USER=self.user.name,
                USER_ID=self.user_ids[self.user.name],
                HOME=self.homedir
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
        container = yield self.get_container()
        if not container:
            self.log.warn("container not found")
            raise gen.Return(0)
        status = container['Status']
        self.log.debug("Container %s status: %s", self.container_id[:7], status)
        parts = status.split()
        # status examples:
        # 'Exited (127) 12 days ago'
        # 'Up 4 days'
        # 'Up 4 days (Paused)' <- TODO: this isn't handled
        # e.g.
        if parts[0] == 'Up':
            raise gen.Return(None)
        elif parts[0] == 'Exited':
            raise gen.Return(int(parts[1][1:-1]))
        else:
            raise ValueError("Unhandled status: '%s'" % status)

    @gen.coroutine
    def get_container(self):
        if not self.container_id:
            return
        self.log.debug("Getting container %s", self.container_id[:7])
        containers = yield self.docker('containers', all=True)
        for c in containers:
            if c['Id'] == self.container_id:
                raise gen.Return(c)
        self.log.info("Container %s is gone", self.container_id[:7])
        # my container is gone, forget my id
        self.container_id = ''
    
    @gen.coroutine
    def start(self, image=None):
        """start the single-user server in a docker container"""
        container = yield self.get_container()
        if container is None:
            if self.system_users:
                extra_kwargs = dict(
                    working_dir=self.homedir,
                    name=self.user.name
                )
            else:
                extra_kwargs = {}

            image = image or self.container_image
            resp = yield self.docker(
                'create_container',
                image=image,
                environment=self.env,
                volumes=self.volume_mount_points,
                **extra_kwargs
            )
            self.container_id = resp['Id']
            self.log.info("Created container %s (%s)", self.container_id[:7], image)
        else:
            self.log.info("Found existing container %s", self.container_id[:7])

        # TODO: handle unpause
        self.log.info("Starting container %s", self.container_id[:7])
        yield self.docker(
            'start',
            self.container_id,
            binds=self.volume_binds,
            port_bindings={8888: (self.container_ip,)},
        )
        resp = yield self.docker('port', self.container_id, 8888)
        self.user.server.port = resp[0]['HostPort']
    
    @gen.coroutine
    def stop(self, now=False):
        """Stop the container
        
        Consider using pause/unpause when docker-py adds support
        """
        self.log.info("Stopping container %s", self.container_id[:7])
        yield self.docker('stop', self.container_id)
        self.clear_state()
