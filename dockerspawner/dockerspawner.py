"""
A Spawner for JupyterHub that runs each user's server in a separate docker container
"""
import itertools
import os
from textwrap import dedent
from concurrent.futures import ThreadPoolExecutor
from pprint import pformat

import docker
from docker.errors import APIError
from tornado import gen

from jupyterhub.spawner import Spawner
from IPython.utils.traitlets import (
    Dict,
    Unicode,
    Bool
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
            if self.tls:
                tls_config = True
            elif self.tls_verify or self.tls_ca or self.tls_client:
                tls_config = docker.tls.TLSConfig(
                    client_cert=self.tls_client,
                    ca_cert=self.tls_ca,
                    verify=self.tls_verify)
            else:
                tls_config = None

            docker_host = os.environ.get('DOCKER_HOST', 'unix://var/run/docker.sock')
            cls._client = docker.Client(base_url=docker_host, tls=tls_config)
        return cls._client

    container_id = Unicode()
    container_ip = Unicode('127.0.0.1', config=True)
    container_image = Unicode("jupyter/singleuser", config=True)
    container_prefix = Unicode(
        "jupyter",
        config=True,
        help=dedent(
            """
            Prefix for container names. The full container name for a particular
            user will be <prefix>-<username>.
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

    tls = Bool(False, config=True, help="If True, connect to docker with --tls")
    tls_verify = Bool(False, config=True, help="If True, connect to docker with --tlsverify")
    tls_ca = Unicode("", config=True, help="Path to CA certificate for docker TLS")
    tls_cert = Unicode("", config=True, help="Path to client certificate for docker TLS")
    tls_key = Unicode("", config=True, help="Path to client key for docker TLS")

    remove_containers = Bool(False, config=True, help="If True, delete containers after they are stopped.")
    extra_create_kwargs = Dict(config=True, help="Additional args to pass for container create")
    extra_start_kwargs = Dict(config=True, help="Additional args to pass for container start")

    @property
    def tls_client(self):
        """A tuple consisting of the TLS client certificate and key if they
        have been provided, otherwise None.

        """
        if self.tls_cert and self.tls_key:
            return (self.tls_cert, self.tls_key)
        return None

    @property
    def volume_mount_points(self):
        """
        Volumes are declared in docker-py in two stages.  First, you declare
        all the locations where you're going to mount volumes when you call
        create_container.

        Returns a list of all the values in self.volumes or
        self.read_only_volumes.
        """
        return list(
            itertools.chain(
                self.volumes.values(),
                self.read_only_volumes.values(),
            )
        )

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
        return volumes

    @property
    def container_name(self):
        return "{}-{}".format(self.container_prefix, self.user.name)

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
            return ""

        container_state = container['State']
        self.log.debug(
            "Container %s status: %s",
            self.container_id[:7],
            pformat(container_state),
        )

        if container_state["Running"]:
            return None
        else:
            return (
                "ExitCode={ExitCode}, "
                "Error='{Error}', "
                "FinishedAt={FinishedAt}".format(**container_state)
            )

    @gen.coroutine
    def get_container(self):
        self.log.debug("Getting container '%s'", self.container_name)
        try:
            container = yield self.docker(
                'inspect_container', self.container_name
            )
            self.container_id = container['Id']
        except APIError as e:
            if e.response.status_code == 404:
                self.log.info("Container '%s' is gone", self.container_name)
                container = None
                # my container is gone, forget my id
                self.container_id = ''
            else:
                raise
        return container

    @gen.coroutine
    def start(self, image=None, extra_create_kwargs=None,
        extra_start_kwargs=None):
        """Start the single-user server in a docker container. You can override
        the default parameters passed to `create_container` through the
        `extra_create_kwargs` dictionary and passed to `start` through the
        `extra_start_kwargs` dictionary.

        Per-instance `extra_create_kwargs` and `extra_start_kwargs` takes
        precedence over their global counterparts.

        """
        container = yield self.get_container()
        if container is None:
            image = image or self.container_image

            # build the dictionary of keyword arguments for create_container
            create_kwargs = dict(
                image=image,
                environment=self.env,
                volumes=self.volume_mount_points,
                name=self.container_name)
            create_kwargs.update(self.extra_create_kwargs)
            if extra_create_kwargs:
                create_kwargs.update(extra_create_kwargs)

            # create the container
            resp = yield self.docker('create_container', **create_kwargs)
            self.container_id = resp['Id']
            self.log.info(
                "Created container '%s' (id: %s) from image %s",
                self.container_name, self.container_id[:7], image)

        else:
            self.log.info(
                "Found existing container '%s' (id: %s)",
                self.container_name, self.container_id[:7])

        # TODO: handle unpause
        self.log.info(
            "Starting container '%s' (id: %s)",
            self.container_name, self.container_id[:7])

        # build the dictionary of keyword arguments for start
        start_kwargs = dict(
            binds=self.volume_binds,
            port_bindings={8888: (self.container_ip,)})
        start_kwargs.update(self.extra_start_kwargs)
        if extra_start_kwargs:
            start_kwargs.update(extra_start_kwargs)

        # start the container
        yield self.docker('start', self.container_id, **start_kwargs)

        # get the public-facing port
        resp = yield self.docker('port', self.container_id, 8888)
        self.user.server.port = resp[0]['HostPort']

    @gen.coroutine
    def stop(self, now=False):
        """Stop the container

        Consider using pause/unpause when docker-py adds support
        """
        self.log.info(
            "Stopping container %s (id: %s)",
            self.container_name, self.container_id[:7])
        yield self.docker('stop', self.container_id)

        if self.remove_containers:
            self.log.info(
                "Removing container %s (id: %s)",
                self.container_name, self.container_id[:7])
            # remove the container, as well as any associated volumes
            yield self.docker('remove_container', self.container_id, v=True)

        self.clear_state()
