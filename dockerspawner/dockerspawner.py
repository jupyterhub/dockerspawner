"""
A Spawner for JupyterHub that runs each user's server in a separate docker container
"""

from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import os
from pprint import pformat
import string
from tarfile import TarFile, TarInfo
from textwrap import dedent
from urllib.parse import urlparse
import warnings

import docker
from docker.errors import APIError
from docker.utils import kwargs_from_env
from tornado import gen, web

from escapism import escape
from jupyterhub.spawner import Spawner
from traitlets import (
    Any,
    Bool,
    CaselessStrEnum,
    Dict,
    List,
    Int,
    Unicode,
    Union,
    default,
    observe,
    validate,
)

from .volumenamingstrategy import default_format_volume_name


class UnicodeOrFalse(Unicode):
    info_text = "a unicode string or False"

    def validate(self, obj, value):
        if value is False:
            return value

        return super(UnicodeOrFalse, self).validate(obj, value)


import jupyterhub

_jupyterhub_xy = "%i.%i" % (jupyterhub.version_info[:2])


class DockerSpawner(Spawner):
    """A Spawner for JupyterHub that runs each user's server in a separate docker container"""

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
            kwargs = {"version": "auto"}
            if self.tls_config:
                kwargs["tls"] = docker.tls.TLSConfig(**self.tls_config)
            kwargs.update(kwargs_from_env())
            kwargs.update(self.client_kwargs)
            client = docker.APIClient(**kwargs)
            cls._client = client
        return cls._client

    # notice when user has set the command
    # default command is that of the container,
    # but user can override it via config
    _user_set_cmd = False

    @observe("cmd")
    def _cmd_changed(self, change):
        self._user_set_cmd = True

    object_id = Unicode()
    # the type of object we create
    object_type = "container"
    # the field containing the object id
    object_id_key = "Id"

    @property
    def container_id(self):
        """alias for object_id"""
        return self.object_id

    @property
    def container_name(self):
        """alias for object_name"""
        return self.object_name

    # deprecate misleading container_ip, since
    # it is not the ip in the container,
    # but the host ip of the port forwarded to the container
    # when use_internal_ip is False
    container_ip = Unicode("127.0.0.1", config=True)

    @observe("container_ip")
    def _container_ip_deprecated(self, change):
        self.log.warning(
            "DockerSpawner.container_ip is deprecated in dockerspawner-0.9."
            "  Use DockerSpawner.host_ip to specify the host ip that is forwarded to the container"
        )
        self.host_ip = change.new

    host_ip = Unicode(
        "127.0.0.1",
        help="""The ip address on the host on which to expose the container's port

        Typically 127.0.0.1, but can be public interfaces as well
        in cases where the Hub and/or proxy are on different machines
        from the user containers.

        Only used when use_internal_ip = False.
        """,
        config=True,
    )

    @default('host_ip')
    def _default_host_ip(self):
        docker_host = os.getenv('DOCKER_HOST')
        if docker_host:
            urlinfo = urlparse(docker_host)
            if urlinfo.scheme == 'tcp':
                return urlinfo.hostname
        return '127.0.0.1'

    # unlike container_ip, container_port is the internal port
    # on which the server is bound.
    container_port = Int(8888, min=1, max=65535, config=True)

    @observe("container_port")
    def _container_port_changed(self, change):
        self.log.warning(
            "DockerSpawner.container_port is deprecated in dockerspawner 0.9."
            "  Use DockerSpawner.port"
        )
        self.port = change.new

    # fix default port to 8888, used in the container

    @default("port")
    def _port_default(self):
        return 8888

    # default to listening on all-interfaces in the container

    @default("ip")
    def _ip_default(self):
        return "0.0.0.0"

    container_image = Unicode("jupyterhub/singleuser:%s" % _jupyterhub_xy, config=True)

    @observe("container_image")
    def _container_image_changed(self, change):
        self.log.warning(
            "DockerSpawner.container_image is deprecated in dockerspawner 0.9."
            "  Use DockerSpawner.image"
        )
        self.image = change.new

    image = Unicode(
        "jupyterhub/singleuser:%s" % _jupyterhub_xy,
        config=True,
        help="""The image to use for single-user servers.

        This image should have the same version of jupyterhub as
        the Hub itself installed.

        If the default command of the image does not launch
        jupyterhub-singleuser, set `c.Spawner.cmd` to
        launch jupyterhub-singleuser, e.g.

        Any of the jupyter docker-stacks should work without additional config,
        as long as the version of jupyterhub in the image is compatible.
        """,
    )

    image_whitelist = Union(
        [Any(), Dict(), List()],
        default_value={},
        config=True,
        help="""
        List or dict of images that users can run.

        If specified, users will be presented with a form
        from which they can select an image to run.

        If a dictionary, the keys will be the options presented to users
        and the values the actual images that will be launched.

        If a list, will be cast to a dictionary where keys and values are the same
        (i.e. a shortcut for presenting the actual images directly to users).

        If a callable, will be called with the Spawner instance as its only argument.
        The user is accessible as spawner.user.
        The callable should return a dict or list as above.
        """,
    )

    @validate('image_whitelist')
    def _image_whitelist_dict(self, proposal):
        """cast image_whitelist to a dict

        If passing a list, cast it to a {item:item}
        dict where the keys and values are the same.
        """
        whitelist = proposal.value
        if isinstance(whitelist, list):
            whitelist = {item: item for item in whitelist}
        return whitelist

    def _get_image_whitelist(self):
        """Evaluate image_whitelist callable

        Or return the whitelist as-is if it's already a dict
        """
        if callable(self.image_whitelist):
            whitelist = self.image_whitelist(self)
            if not isinstance(whitelist, dict):
                # always return a dict
                whitelist = {item: item for item in whitelist}
            return whitelist
        return self.image_whitelist

    @default('options_form')
    def _default_options_form(self):
        image_whitelist = self._get_image_whitelist()
        if len(image_whitelist) <= 1:
            # default form only when there are images to choose from
            return ''
        # form derived from wrapspawner.ProfileSpawner
        option_t = '<option value="{image}" {selected}>{image}</option>'
        options = [
            option_t.format(
                image=image, selected='selected' if image == self.image else ''
            )
            for image in image_whitelist
        ]
        return """
        <label for="image">Select an image:</label>
        <select class="form-control" name="image" required autofocus>
        {options}
        </select>
        """.format(
            options=options
        )

    def options_from_form(self, formdata):
        """Turn options formdata into user_options"""
        options = {}
        if 'image' in formdata:
            options['image'] = formdata['image'][0]
        return options

    pull_policy = CaselessStrEnum(
        ["always", "ifnotpresent", "never"],
        default_value="ifnotpresent",
        config=True,
        help="""The policy for pulling the user docker image.

        Choices:

        - ifnotpresent: pull if the image is not already present (default)
        - always: always pull the image to check for updates, even if it is present
        - never: never perform a pull
        """
    )

    container_prefix = Unicode(config=True, help="DEPRECATED in 0.10. Use prefix")

    container_name_template = Unicode(
        config=True, help="DEPRECATED in 0.10. Use name_template"
    )

    @observe("container_name_template", "container_prefix")
    def _deprecate_container_alias(self, change):
        new_name = change.name[len("container_") :]
        setattr(self, new_name, change.new)

    prefix = Unicode(
        "jupyter",
        config=True,
        help=dedent(
            """
            Prefix for container names. See name_template for full container name for a particular
            user's server.
            """
        ),
    )

    name_template = Unicode(
        "{prefix}-{username}",
        config=True,
        help=dedent(
            """
            Name of the container or service: with {username}, {imagename}, {prefix} replacements.
            {raw_username} can be used for the original, not escaped username
            (may contain uppercase, special characters).
            The default name_template is <prefix>-<username> for backward compatibility.
            """
        ),
    )

    client_kwargs = Dict(
        config=True,
        help="Extra keyword arguments to pass to the docker.Client constructor.",
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
        ),
    )

    move_certs_image = Unicode(
        "busybox:1.30.1",
        config=True,
        help="""The image used to stage internal SSL certificates.

        Busybox is used because we just need an empty container
        that waits while we stage files into the volume via .put_archive.
        """
    )

    @gen.coroutine
    def move_certs(self, paths):
        self.log.info("Staging internal ssl certs for %s", self._log_name)
        yield self.pull_image(self.move_certs_image)
        # create the volume
        volume_name = self.format_volume_name(self.certs_volume_name, self)
        # create volume passes even if it already exists
        self.log.info("Creating ssl volume %s for %s", volume_name, self._log_name)
        yield self.docker('create_volume', volume_name)

        # create a tar archive of the internal cert files
        # docker.put_archive takes a tarfile and a running container
        # and unpacks the archive into the container
        nb_paths = {}
        tar_buf = BytesIO()
        archive = TarFile(fileobj=tar_buf, mode='w')
        for key, hub_path in paths.items():
            fname = os.path.basename(hub_path)
            nb_paths[key] = '/certs/' + fname
            with open(hub_path, 'rb') as f:
                content = f.read()
            tarinfo = TarInfo(name=fname)
            tarinfo.size = len(content)
            tarinfo.mtime = os.stat(hub_path).st_mtime
            tarinfo.mode = 0o644
            archive.addfile(tarinfo, BytesIO(content))
        archive.close()
        tar_buf.seek(0)

        # run a container to stage the certs,
        # mounting the volume at /certs/
        host_config = self.client.create_host_config(
            binds={
                volume_name: {"bind": "/certs", "mode": "rw"},
            },
        )
        container = yield self.docker('create_container',
            self.move_certs_image,
            volumes=["/certs"],
            host_config=host_config,
        )

        container_id = container['Id']
        self.log.debug(
            "Container %s is creating ssl certs for %s",
            container_id[:12], self._log_name,
        )
        # start the container
        yield self.docker('start', container_id)
        # stage the archive to the container
        try:
            yield self.docker(
                'put_archive',
                container=container_id,
                path='/certs',
                data=tar_buf,
            )
        finally:
            yield self.docker('remove_container', container_id)
        return nb_paths

    certs_volume_name = Unicode(
        "{prefix}ssl-{username}",
        config=True,
        help="""Volume name

        The same string-templating applies to this
        as other volume names.
        """
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
        ),
    )

    format_volume_name = Any(
        help="""Any callable that accepts a string template and a DockerSpawner instance as parameters in that order and returns a string.

        Reusable implementations should go in dockerspawner.VolumeNamingStrategy, tests should go in ...
        """
    ).tag(config=True)

    @default("format_volume_name")
    def _get_default_format_volume_name(self):
        return default_format_volume_name

    use_docker_client_env = Bool(
        True,
        config=True,
        help="DEPRECATED. Docker env variables are always used if present.",
    )

    @observe("use_docker_client_env")
    def _client_env_changed(self):
        self.log.warning(
            "DockerSpawner.use_docker_client_env is deprecated and ignored."
            "  Docker environment variables are always used if defined."
        )

    tls_config = Dict(
        config=True,
        help="""Arguments to pass to docker TLS configuration.

        See docker.client.TLSConfig constructor for options.
        """,
    )
    tls = tls_verify = tls_ca = tls_cert = tls_key = tls_assert_hostname = Any(
        config=True,
        help="""DEPRECATED. Use DockerSpawner.tls_config dict to set any TLS options.""",
    )

    @observe(
        "tls", "tls_verify", "tls_ca", "tls_cert", "tls_key", "tls_assert_hostname"
    )
    def _tls_changed(self, change):
        self.log.warning(
            "%s config ignored, use %s.tls_config dict to set full TLS configuration.",
            change.name,
            self.__class__.__name__,
        )

    remove_containers = Bool(
        False, config=True, help="DEPRECATED in DockerSpawner 0.10. Use .remove"
    )

    @observe("remove_containers")
    def _deprecate_remove_containers(self, change):
        # preserve remove_containers alias to .remove
        self.remove = change.new

    remove = Bool(
        False,
        config=True,
        help="""
        If True, delete containers when servers are stopped.

        This will destroy any data in the container not stored in mounted volumes.
        """,
    )

    @property
    def will_resume(self):
        # indicate that we will resume,
        # so JupyterHub >= 0.7.1 won't cleanup our API token
        return not self.remove

    extra_create_kwargs = Dict(
        config=True, help="Additional args to pass for container create"
    )
    extra_host_config = Dict(
        config=True, help="Additional args to create_host_config for container create"
    )

    _docker_safe_chars = set(string.ascii_letters + string.digits + "-")
    _docker_escape_char = "_"

    hub_ip_connect = Unicode(
        config=True,
        help=dedent(
            """
            If set, DockerSpawner will configure the containers to use
            the specified IP to connect the hub api.  This is useful
            when the hub_api is bound to listen on all ports or is
            running inside of a container.
            """
        ),
    )

    @observe("hub_ip_connect")
    def _ip_connect_changed(self, change):
        if jupyterhub.version_info >= (0, 8):
            warnings.warn(
                "DockerSpawner.hub_ip_connect is no longer needed with JupyterHub 0.8."
                "  Use JupyterHub.hub_connect_ip instead.",
                DeprecationWarning,
            )

    use_internal_ip = Bool(
        False,
        config=True,
        help=dedent(
            """
            Enable the usage of the internal docker ip. This is useful if you are running
            jupyterhub (as a container) and the user containers within the same docker network.
            E.g. by mounting the docker socket of the host into the jupyterhub container.
            Default is True if using a docker network, False if bridge or host networking is used.
            """
        ),
    )

    @default("use_internal_ip")
    def _default_use_ip(self):
        # setting network_name to something other than bridge or host implies use_internal_ip
        if self.network_name not in {"bridge", "host"}:
            return True

        else:
            return False

    use_internal_hostname = Bool(
        False,
        config=True,
        help=dedent(
            """
            Use the docker hostname for connecting.

            instead of an IP address.
            This should work in general when using docker networks,
            and must be used when internal_ssl is enabled.
            It is enabled by default if internal_ssl is enabled.
            """
        ),
    )

    @default("use_internal_hostname")
    def _default_use_hostname(self):
        # FIXME: replace getattr with self.internal_ssl
        # when minimum jupyterhub is 1.0
        return getattr(self, 'internal_ssl', False)

    links = Dict(
        config=True,
        help=dedent(
            """
            Specify docker link mapping to add to the container, e.g.

                links = {'jupyterhub': 'jupyterhub'}

            If the Hub is running in a Docker container,
            this can simplify routing because all traffic will be using docker hostnames.
            """
        ),
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
        ),
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
        return sorted([value["bind"] for value in self.volume_binds.values()])

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
        read_only_volumes = {}
        # FIXME: replace getattr with self.internal_ssl
        # when minimum jupyterhub is 1.0
        if getattr(self, 'internal_ssl', False):
            # add SSL volume as read-only
            read_only_volumes[self.certs_volume_name] = '/certs'
        read_only_volumes.update(self.read_only_volumes)
        return self._volumes_to_binds(read_only_volumes, binds, mode="ro")

    _escaped_name = None

    @property
    def escaped_name(self):
        """Escape the username so it's safe for docker objects"""
        if self._escaped_name is None:
            self._escaped_name = self._escape(self.user.name)
        return self._escaped_name

    def _escape(self, s):
        """Escape a string to docker-safe characters"""
        return escape(
            s,
            safe=self._docker_safe_chars,
            escape_char=self._docker_escape_char,
        )

    object_id = Unicode(allow_none=True)

    def template_namespace(self):
        escaped_image = self.image.replace("/", "_")
        server_name = getattr(self, "name", "")
        return {
            "username": self.escaped_name,
            "safe_username": self.user.name,
            "raw_username": self.user.name,
            "imagename": escaped_image,
            "servername": server_name,
            "prefix": self.prefix,
        }

    @property
    def object_name(self):
        """Render the name of our container/service using name_template"""
        return self.name_template.format(**self.template_namespace())

    def load_state(self, state):
        super(DockerSpawner, self).load_state(state)
        if "container_id" in state:
            # backward-compatibility for dockerspawner < 0.10
            self.object_id = state.get("container_id")
        else:
            self.object_id = state.get("object_id", "")

    def get_state(self):
        state = super(DockerSpawner, self).get_state()
        if self.object_id:
            state["object_id"] = self.object_id
        return state

    def _public_hub_api_url(self):
        proto, path = self.hub.api_url.split("://", 1)
        ip, rest = path.split(":", 1)
        return "{proto}://{ip}:{rest}".format(
            proto=proto, ip=self.hub_ip_connect, rest=rest
        )

    def _env_keep_default(self):
        """Don't inherit any env from the parent process"""
        return []

    def get_args(self):
        args = super().get_args()
        if self.hub_ip_connect:
            # JupyterHub 0.7 specifies --hub-api-url
            # on the command-line, which is hard to update
            for idx, arg in enumerate(list(args)):
                if arg.startswith("--hub-api-url="):
                    args.pop(idx)
                    break

            args.append("--hub-api-url=%s" % self._public_hub_api_url())
        return args

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
        container = yield self.get_object()
        if not container:
            self.log.warning("Container not found: %s", self.container_name)
            return 0

        container_state = container["State"]
        self.log.debug(
            "Container %s status: %s", self.container_id[:7], pformat(container_state)
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
    def get_object(self):
        self.log.debug("Getting container '%s'", self.object_name)
        try:
            obj = yield self.docker("inspect_%s" % self.object_type, self.object_name)
            self.object_id = obj[self.object_id_key]
        except APIError as e:
            if e.response.status_code == 404:
                self.log.info(
                    "%s '%s' is gone", self.object_type.title(), self.object_name
                )
                obj = None
                # my container is gone, forget my id
                self.object_id = ""
            elif e.response.status_code == 500:
                self.log.info(
                    "%s '%s' is on unhealthy node",
                    self.object_type.title(),
                    self.object_name,
                )
                obj = None
                # my container is unhealthy, forget my id
                self.object_id = ""
            else:
                raise

        return obj

    @gen.coroutine
    def get_command(self):
        """Get the command to run (full command + args)"""
        if self._user_set_cmd:
            cmd = self.cmd
        else:
            image_info = yield self.docker("inspect_image", self.image)
            cmd = image_info["Config"]["Cmd"]
        return cmd + self.get_args()

    @gen.coroutine
    def remove_object(self):
        self.log.info("Removing %s %s", self.object_type, self.object_id)
        # remove the container, as well as any associated volumes
        try:
            yield self.docker("remove_" + self.object_type, self.object_id, v=True)
        except docker.errors.APIError as e:
            if e.status_code == 409:
                self.log.debug("Already removing %s: %s", self.object_type, self.object_id)
            else:
                raise

    @gen.coroutine
    def check_image_whitelist(self, image):
        image_whitelist = self._get_image_whitelist()
        if not image_whitelist:
            return image
        if image not in image_whitelist:
            raise web.HTTPError(
                400,
                "Image %s not in whitelist: %s" % (image, ', '.join(image_whitelist)),
            )
        # resolve image alias to actual image name
        return image_whitelist[image]

    @default('ssl_alt_names')
    def _get_ssl_alt_names(self):
        return ['DNS:' + self.internal_hostname]

    @gen.coroutine
    def create_object(self):
        """Create the container/service object"""

        create_kwargs = dict(
            image=self.image,
            environment=self.get_env(),
            volumes=self.volume_mount_points,
            name=self.container_name,
            command=(yield self.get_command()),
        )

        # ensure internal port is exposed
        create_kwargs["ports"] = {"%i/tcp" % self.port: None}

        create_kwargs.update(self.extra_create_kwargs)

        # build the dictionary of keyword arguments for host_config
        host_config = dict(binds=self.volume_binds, links=self.links)

        if getattr(self, "mem_limit", None) is not None:
            # If jupyterhub version > 0.7, mem_limit is a traitlet that can
            # be directly configured. If so, use it to set mem_limit.
            # this will still be overriden by extra_host_config
            host_config["mem_limit"] = self.mem_limit

        if not self.use_internal_ip:
            host_config["port_bindings"] = {self.port: (self.host_ip,)}
        host_config.update(self.extra_host_config)
        host_config.setdefault("network_mode", self.network_name)

        self.log.debug("Starting host with config: %s", host_config)

        host_config = self.client.create_host_config(**host_config)
        create_kwargs.setdefault("host_config", {}).update(host_config)

        # create the container
        obj = yield self.docker("create_container", **create_kwargs)
        return obj

    @gen.coroutine
    def start_object(self):
        """Actually start the container/service

        e.g. calling `docker start`
        """
        return self.docker("start", self.container_id)

    @gen.coroutine
    def stop_object(self):
        """Stop the container/service

        e.g. calling `docker stop`. Does not remove the container.
        """
        return self.docker("stop", self.container_id)


    @gen.coroutine
    def pull_image(self, image):
        """Pull the image, if needed

        - pulls it unconditionally if pull_policy == 'always'
        - otherwise, checks if it exists, and
          - raises if pull_policy == 'never'
          - pulls if pull_policy == 'ifnotpresent'
        """
        # docker wants to split repo:tag
        if ':' in image:
            repo, tag = image.split(':', 1)
        else:
            repo = image
            tag = 'latest'

        if self.pull_policy.lower() == 'always':
            # always pull
            self.log.info("pulling %s", image)
            yield self.docker('pull', repo, tag)
            # done
            return
        try:
            # check if the image is present
            yield self.docker('inspect_image', image)
        except docker.errors.NotFound:
            if self.pull_policy == "never":
                # never pull, raise because there is no such image
                raise
            elif self.pull_policy == "ifnotpresent":
                # not present, pull it for the first time
                self.log.info("pulling image %s", image)
                yield self.docker('pull', repo, tag)

    @gen.coroutine
    def start(self, image=None, extra_create_kwargs=None, extra_host_config=None):
        """Start the single-user server in a docker container.

        Additional arguments to create/host config/etc. can be specified
        via .extra_create_kwargs and .extra_host_config attributes.

        If the container exists and `c.DockerSpawner.remove` is true, then
        the container is removed first. Otherwise, the existing containers
        will be restarted.
        """

        if image:
            self.log.warning("Specifying image via .start args is deprecated")
            self.image = image
        if extra_create_kwargs:
            self.log.warning(
                "Specifying extra_create_kwargs via .start args is deprecated"
            )
            self.extra_create_kwargs.update(extra_create_kwargs)
        if extra_host_config:
            self.log.warning(
                "Specifying extra_host_config via .start args is deprecated"
            )
            self.extra_host_config.update(extra_host_config)

        # image priority:
        # 1. user options (from spawn options form)
        # 2. self.image from config
        image_option = self.user_options.get('image')
        if image_option:
            # save choice in self.image
            self.image = yield self.check_image_whitelist(image_option)

        image = self.image
        yield self.pull_image(image)

        obj = yield self.get_object()
        if obj and self.remove:
            self.log.warning(
                "Removing %s that should have been cleaned up: %s (id: %s)",
                self.object_type,
                self.object_name,
                self.object_id[:7],
            )
            yield self.remove_object()

            obj = None

        if obj is None:
            obj = yield self.create_object()
            self.object_id = obj[self.object_id_key]
            self.log.info(
                "Created %s %s (id: %s) from image %s",
                self.object_type,
                self.object_name,
                self.object_id[:7],
                self.image,
            )

        else:
            self.log.info(
                "Found existing %s %s (id: %s)",
                self.object_type,
                self.object_name,
                self.object_id[:7],
            )
            # Handle re-using API token.
            # Get the API token from the environment variables
            # of the running container:
            for line in obj["Config"]["Env"]:
                if line.startswith(("JPY_API_TOKEN=", "JUPYTERHUB_API_TOKEN=")):
                    self.api_token = line.split("=", 1)[1]
                    break

        # TODO: handle unpause
        self.log.info(
            "Starting %s %s (id: %s)",
            self.object_type,
            self.object_name,
            self.container_id[:7],
        )

        # start the container
        yield self.start_object()

        ip, port = yield self.get_ip_and_port()
        if jupyterhub.version_info < (0, 7):
            # store on user for pre-jupyterhub-0.7:
            self.user.server.ip = ip
            self.user.server.port = port
        # jupyterhub 0.7 prefers returning ip, port:
        return (ip, port)

    @property
    def internal_hostname(self):
        """Return our hostname

        used with internal SSL
        """
        return self.container_name

    @gen.coroutine
    def get_ip_and_port(self):
        """Queries Docker daemon for container's IP and port.

        If you are using network_mode=host, you will need to override
        this method as follows::

            @gen.coroutine
            def get_ip_and_port(self):
                return self.host_ip, self.port

        You will need to make sure host_ip and port
        are correct, which depends on the route to the container
        and the port it opens.
        """
        if self.use_internal_hostname:
            # internal ssl uses hostnames,
            # required for domain-name matching with internal SSL
            # TODO: should we always do this?
            # are there any cases where internal_ip works
            # and internal_hostname doesn't?
            ip = self.internal_hostname
            port = self.port
        elif self.use_internal_ip:
            resp = yield self.docker("inspect_container", self.container_id)
            network_settings = resp["NetworkSettings"]
            if "Networks" in network_settings:
                ip = self.get_network_ip(network_settings)
            else:  # Fallback for old versions of docker (<1.9) without network management
                ip = network_settings["IPAddress"]
            port = self.port
        else:
            resp = yield self.docker("port", self.container_id, self.port)
            if resp is None:
                raise RuntimeError("Failed to get port info for %s" % self.container_id)

            ip = resp[0]["HostIp"]
            port = int(resp[0]["HostPort"])

        if ip == "0.0.0.0":
            ip = urlparse(self.client.base_url).hostname
            if ip == "localnpipe":
                ip = "localhost"

        return ip, port

    def get_network_ip(self, network_settings):
        networks = network_settings["Networks"]
        if self.network_name not in networks:
            raise Exception(
                "Unknown docker network '{network}'."
                " Did you create it with `docker network create <name>`?".format(
                    network=self.network_name
                )
            )

        network = networks[self.network_name]
        ip = network["IPAddress"]
        return ip

    @gen.coroutine
    def stop(self, now=False):
        """Stop the container

        Will remove the container if `c.DockerSpawner.remove` is `True`.

        Consider using pause/unpause when docker-py adds support.
        """
        self.log.info(
            "Stopping %s %s (id: %s)",
            self.object_type,
            self.object_name,
            self.object_id[:7],
        )
        yield self.stop_object()

        if self.remove:
            yield self.remove_object()

        self.clear_state()

    def _volumes_to_binds(self, volumes, binds, mode="rw"):
        """Extract the volume mount points from volumes property.

        Returns a dict of dict entries of the form::

            {'/host/dir': {'bind': '/guest/dir': 'mode': 'rw'}}
        """

        def _fmt(v):
            return self.format_volume_name(v, self)

        for k, v in volumes.items():
            m = mode
            if isinstance(v, dict):
                if "mode" in v:
                    m = v["mode"]
                v = v["bind"]
            binds[_fmt(k)] = {"bind": _fmt(v), "mode": m}
        return binds
