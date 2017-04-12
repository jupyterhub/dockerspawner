"""
A Spawner for JupyterHub that runs each user's server in a separate docker container
"""

import string
from textwrap import dedent
from concurrent.futures import ThreadPoolExecutor
from pprint import pformat

import docker
from docker.errors import APIError
from docker.utils import kwargs_from_env
from tornado import gen

from escapism import escape
from jupyterhub.spawner import Spawner
from traitlets import (
    Dict,
    Unicode,
    Bool,
    Int,
    Any,
    default,
    observe,
)

from .volumenamingstrategy import default_format_volume_name

class UnicodeOrFalse(Unicode):
    info_text = 'a unicode string or False'
    def validate(self, obj, value):
        if value is False:
            return value
        return super(UnicodeOrFalse, self).validate(obj, value)

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
            kwargs = {}
            if self.tls_config:
                kwargs['tls'] = docker.tls.TLSConfig(**self.tls_config)
            kwargs.update(kwargs_from_env())
            client = docker.APIClient(version='auto', **kwargs)
            cls._client = client
        return cls._client

    container_id = Unicode()
    container_ip = Unicode('127.0.0.1', config=True)
    container_port = Int(8888, min=1, max=65535, config=True)
    container_image = Unicode("jupyterhub/singleuser", config=True)
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
            Map from host file/directory to container (guest) file/directory
            mount point and (optionally) a mode. When specifying the
            guest mount point (bind) for the volume, you may use a
            dict or str. If a str, then the volume will default to a
            read-write (mode="rw"). With a dict, the bind is
            identified by "bind" and the "mode" may be one of "rw"
            (default), "ro" (read-only), "z" (public/shared SELinux
            volume label), and "Z" (private/unshared SELinux volume
            label).

            If format_volume_name is not set,
            default_format_volume_name is used for naming volumes.
            In this case, if you use {username} in either the host or guest
            file/directory path, it will be replaced with the current
            user's name.
            """
        )
    )

    read_only_volumes = Dict(
        config=True,
        help=dedent(
            """
            Map from host file/directory to container file/directory.
            Volumes specified here will be read-only in the container.

            If format_volume_name is not set,
            default_format_volume_name is used for naming volumes.
            In this case, if you use {username} in either the host or guest
            file/directory path, it will be replaced with the current
            user's name.
            """
        )
    )

    format_volume_name = Any(
        help="""Any callable that accepts a string template and a DockerSpawner instance as parameters in that order and returns a string.

        Reusable implementations should go in dockerspawner.VolumeNamingStrategy, tests should go in ...
        """
    ).tag(config=True)

    def default_format_volume_name(template, spawner):
        return template.format(username=spawner.user.name)

    @default('format_volume_name')
    def _get_default_format_volume_name(self):
        return default_format_volume_name

    use_docker_client_env = Bool(True, config=True,
        help="DEPRECATED. Docker env variables are always used if present.")
    @observe('use_docker_client_env')
    def _client_env_changed(self):
        self.log.warning("DockerSpawner.use_docker_client_env is deprecated and ignored."
        "  Docker environment variables are always used if defined.")
    tls_config = Dict(config=True,
        help="""Arguments to pass to docker TLS configuration.
        
        See docker.client.TLSConfig constructor for options.
        """
    )
    tls = tls_verify = tls_ca = tls_cert = \
    tls_key = tls_assert_hostname = Any(config=True,
        help="""DEPRECATED. Use DockerSpawner.tls_config dict to set any TLS options."""
    )
    @observe('tls', 'tls_verify', 'tls_ca', 'tls_cert', 'tls_key', 'tls_assert_hostname')
    def _tls_changed(self, change):
        self.log.warning("%s config ignored, use %s.tls_config dict to set full TLS configuration.",
            change.name, self.__class__.__name__,
        )

    remove_containers = Bool(False, config=True, help="If True, delete containers after they are stopped.")
    extra_create_kwargs = Dict(config=True, help="Additional args to pass for container create")
    extra_start_kwargs = Dict(config=True, help="Additional args to pass for container start")
    extra_host_config = Dict(config=True, help="Additional args to create_host_config for container create")

    _container_safe_chars = set(string.ascii_letters + string.digits + '-')
    _container_escape_char = '_'

    hub_ip_connect = Unicode(
        config=True,
        help=dedent(
            """
            If set, DockerSpawner will configure the containers to use
            the specified IP to connect the hub api.  This is useful
            when the hub_api is bound to listen on all ports or is
            running inside of a container.
            """
        )
    )

    use_internal_ip = Bool(False,
        config=True,
        help=dedent(
            """
            Enable the usage of the internal docker ip. This is useful if you are running
            jupyterhub (as a container) and the user containers within the same docker network.
            E.g. by mounting the docker socket of the host into the jupyterhub container.
            Default is True if using a docker network, False if bridge or host networking is used.
            """
        )
    )
    @default('use_internal_ip')
    def _default_use_ip(self):
        # setting network_name to something other than bridge or host implies use_internal_ip
        if self.network_name not in {'bridge', 'host'}:
            return True
        else:
            return False

    links = Dict(
        config=True,
        help=dedent(
            """
            Specify docker link mapping to add to the container, e.g.

                links = {'jupyterhub': 'jupyterhub'}

            If the Hub is running in a Docker container,
            this can simplify routing because all traffic will be using docker hostnames.
            """
        )
    )

    network_name = Unicode(
        "bridge",
        config=True,
        help=dedent(
            """
            Run the containers on this docker network.
            If it is an internal docker network, the Hub should be on the same network,
            as internal docker IP addresses will be used.
            For bridge networking, external ports will be bound.
            """
        )
    )

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
        Returns a sorted list of all the values in self.volumes or
        self.read_only_volumes.
        """
        return sorted([value['bind'] for value in self.volume_binds.values()])

    @property
    def volume_binds(self):
        """
        The second half of declaring a volume with docker-py happens when you
        actually call start().  The required format is a dict of dicts that
        looks like:

        {
            host_location: {'bind': container_location, 'mode': 'rw'}
        }
        mode may be 'ro', 'rw', 'z', or 'Z'.

        """
        binds = self._volumes_to_binds(self.volumes, {})
        return self._volumes_to_binds(self.read_only_volumes, binds, mode='ro')

    _escaped_name = None
    @property
    def escaped_name(self):
        if self._escaped_name is None:
            self._escaped_name = escape(self.user.name,
                safe=self._container_safe_chars,
                escape_char=self._container_escape_char,
            )
        return self._escaped_name

    @property
    def container_name(self):
        return "{}-{}".format(self.container_prefix, self.escaped_name)

    def load_state(self, state):
        super(DockerSpawner, self).load_state(state)
        self.container_id = state.get('container_id', '')

    def get_state(self):
        state = super(DockerSpawner, self).get_state()
        if self.container_id:
            state['container_id'] = self.container_id
        return state

    def _public_hub_api_url(self):
        proto, path = self.hub.api_url.split('://', 1)
        ip, rest = path.split(':', 1)
        return '{proto}://{ip}:{rest}'.format(
            proto = proto,
            ip = self.hub_ip_connect,
            rest = rest
        )

    def _env_keep_default(self):
        """Don't inherit any env from the parent process"""
        return []

    def get_env(self):
        env = super(DockerSpawner, self).get_env()
        env.update(dict(
            JPY_USER=self.user.name,
            JPY_COOKIE_NAME=self.user.server.cookie_name,
            JPY_BASE_URL=self.user.server.base_url,
            JPY_HUB_PREFIX=self.hub.server.base_url
        ))

        if self.notebook_dir:
            env['NOTEBOOK_DIR'] = self.notebook_dir

        if self.hub_ip_connect:
           hub_api_url = self._public_hub_api_url()
        else:
           hub_api_url = self.hub.api_url
        env['JPY_HUB_API_URL'] = hub_api_url

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
            return None 

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
            elif e.response.status_code == 500:
                self.log.info("Container '%s' is on unhealthy node", self.container_name)
                container = None
                # my container is unhealthy, forget my id
                self.container_id = ''
            else:
                raise
        return container

    @gen.coroutine
    def start(self, image=None, extra_create_kwargs=None,
        extra_start_kwargs=None, extra_host_config=None):
        """Start the single-user server in a docker container. You can override
        the default parameters passed to `create_container` through the
        `extra_create_kwargs` dictionary and passed to `start` through the
        `extra_start_kwargs` dictionary.  You can also override the
        'host_config' parameter passed to `create_container` through the
        `extra_host_config` dictionary.

        Per-instance `extra_create_kwargs`, `extra_start_kwargs`, and
        `extra_host_config` take precedence over their global counterparts.

        """
        container = yield self.get_container()
        if container is None:
            image = image or self.container_image

            # build the dictionary of keyword arguments for create_container
            create_kwargs = dict(
                image=image,
                environment=self.get_env(),
                volumes=self.volume_mount_points,
                name=self.container_name,
            )
            create_kwargs.update(self.extra_create_kwargs)
            if extra_create_kwargs:
                create_kwargs.update(extra_create_kwargs)

            # build the dictionary of keyword arguments for host_config
            host_config = dict(binds=self.volume_binds, links=self.links)

            if hasattr(self, 'mem_limit') and self.mem_limit is not None:
                # If jupyterhub version > 0.7, mem_limit is a traitlet that can
                # be directly configured. If so, use it to set mem_limit.
                # this will still be overriden by extra_host_config
                host_config['mem_limit'] = self.mem_limit

            if not self.use_internal_ip:
                host_config['port_bindings'] = {self.container_port: (self.container_ip,)}
            host_config.update(self.extra_host_config)
            host_config.setdefault('network_mode', self.network_name)

            if extra_host_config:
                host_config.update(extra_host_config)

            self.log.debug("Starting host with config: %s", host_config)

            host_config = self.client.create_host_config(**host_config)
            create_kwargs.setdefault('host_config', {}).update(host_config)

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
            # Handle re-using API token.
            # Get the API token from the environment variables
            # of the running container:
            for line in container['Config']['Env']:
                if line.startswith('JPY_API_TOKEN='):
                    self.api_token = line.split('=', 1)[1]
                    break

        # TODO: handle unpause
        self.log.info(
            "Starting container '%s' (id: %s)",
            self.container_name, self.container_id[:7])

        # build the dictionary of keyword arguments for start
        start_kwargs = {}
        start_kwargs.update(self.extra_start_kwargs)
        if extra_start_kwargs:
            start_kwargs.update(extra_start_kwargs)

        # start the container
        yield self.docker('start', self.container_id, **start_kwargs)

        ip, port = yield self.get_ip_and_port()
        # store on user for pre-jupyterhub-0.7:
        self.user.server.ip = ip
        self.user.server.port = port
        # jupyterhub 0.7 prefers returning ip, port:
        return (ip, port)

    @gen.coroutine
    def get_ip_and_port(self):
        """Queries Docker daemon for container's IP and port.

        If you are using network_mode=host, you will need to override
        this method as follows::

            @gen.coroutine
            def get_ip_and_port(self):
                return self.container_ip, self.container_port

        You will need to make sure container_ip and container_port
        are correct, which depends on the route to the container
        and the port it opens.
        """
        if self.use_internal_ip:
            resp = yield self.docker('inspect_container', self.container_id)
            network_settings = resp['NetworkSettings']
            if 'Networks' in network_settings:
                ip = self.get_network_ip(network_settings)
            else:  # Fallback for old versions of docker (<1.9) without network management
                ip = network_settings['IPAddress']
            port = self.container_port
        else:
            resp = yield self.docker('port', self.container_id, self.container_port)
            if resp is None:
                raise RuntimeError("Failed to get port info for %s" % self.container_id)
            ip = resp[0]['HostIp']
            port = resp[0]['HostPort']
        return ip, port

    def get_network_ip(self, network_settings):
        networks = network_settings['Networks']
        if self.network_name not in networks:
            raise Exception(
                "Unknown docker network '{network}'."
                " Did you create it with `docker network create <name>`?".format(
                    network=self.network_name
                )
            )
        network = networks[self.network_name]
        ip = network['IPAddress']
        return ip

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

        # indicate that we will resume,
        # so JupyterHub >= 0.7.1 won't cleanup our API token
        self.will_resume = (not self.remove_containers)

        self.clear_state()

    def _volumes_to_binds(self, volumes, binds, mode='rw'):
        """Extract the volume mount points from volumes property.

        Returns a dict of dict entries of the form::

            {'/host/dir': {'bind': '/guest/dir': 'mode': 'rw'}}
        """
        def _fmt(v):
            return self.format_volume_name(v, self)

        for k, v in volumes.items():
            m = mode
            if isinstance(v, dict):
                if 'mode' in v:
                    m = v['mode']
                v = v['bind']
            binds[_fmt(k)] = {'bind': _fmt(v), 'mode': m}
        return binds


