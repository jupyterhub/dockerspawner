"""
A Spawner for JupyterHub that runs each user's server in a separate docker service
"""

from pprint import pformat
from textwrap import dedent

from docker.types import ContainerSpec, TaskTemplate, Resources, EndpointSpec, Mount, DriverConfig
from docker.errors import APIError
from tornado import gen
from traitlets import (
    Dict,
    Unicode,
    Bool,
    Int,
    Any,
    default,
    observe,
)

from .dockerspawner import DockerSpawner
import jupyterhub


class SwarmSpawner(DockerSpawner):
    """A Spawner for JupyterHub that runs each user's server in a separate docker service"""
    service_id = Unicode()

    service_prefix = Unicode(
        "jupyter",
        config=True,
        help=dedent(
            """
            Prefix for service names. See service_name_template for full service name for a particular
            user.
            """
        )
    )

    service_name_template = Unicode(
        "{prefix}-{username}",
        config=True,
        help=dedent(
            """
            Name of the service: with {username}, {imagename}, {prefix} replacements.
            The default service_name_template is <prefix>-<username> for backward compatibility
            """
        )
    )

    # TODO: relevant anymore within swarmspawner?
    remove_services = Bool(False, config=True, help="If True, delete services after they are stopped.")

    @property
    def will_resume(self):
        # indicate that we will resume,
        # so JupyterHub >= 0.7.1 won't cleanup our API token
        return not self.remove_services

    @property
    def service_name(self):
        escaped_service_image = self.image.replace("/", "_")
        server_name = getattr(self, 'name', '')
        d = {'username': self.escaped_name, 'imagename': escaped_service_image, 'servername': server_name,
             'prefix': self.service_prefix}
        return self.service_name_template.format(**d)

    volume_driver = Unicode(
        "",
        config=True,
        help=dedent(
            """
            Use this driver for mounting the notebook volumes.
            Note that this driver must support multiple hosts in order for it to work across the swarm.
            For a list of possible drivers, see https://docs.docker.com/engine/extend/legacy_plugins/#volume-plugins
            """
        )
    )

    volume_driver_options = Dict(
        config=True,
        help=dedent(
            """
            Configuration options for the multi-host volume driver.
            """
        )
    )

    @property
    def mount_driver_config(self):
        return DriverConfig(name=self.volume_driver, options=self.volume_driver_options or None)

    @property
    def mounts(self):
        if len(self.volume_binds):
            driver = self.mount_driver_config
            return [Mount(target=vol['bind'],
                          source=host_loc,
                          type='bind',
                          read_only=vol['mode'] == 'ro',
                          driver_config=driver)
                    for host_loc, vol in self.volume_binds.items()]
        else:
            return []

    def load_state(self, state):
        super(SwarmSpawner, self).load_state(state)
        self.service_id = state.get('service_id', '')

    def get_state(self):
        state = super(SwarmSpawner, self).get_state()
        if self.service_id:
            state['service_id'] = self.service_id
        return state

    @gen.coroutine
    def poll(self):
        """Check for my id in `docker ps`"""
        service = yield self.get_task()
        if not service:
            self.log.warn("service not found")
            return 0

        service_state = service['Status']
        self.log.debug(
            "Service %s status: %s",
            self.service_id[:7],
            pformat(service_state),
        )

        if service_state['State'] == 'running':
            return None
        else:
            return {k: pformat(v) for k, v in service.items()}

    @gen.coroutine
    def get_service(self):
        self.log.debug("Getting service '%s'", self.service_name)
        try:
            service = yield self.docker(
                'inspect_service', self.service_name
            )
            self.service_id = service['ID']
            # self.log.critical(pformat(service))
        except APIError as e:
            if e.response.status_code == 404:
                self.log.info("Service '%s' is gone", self.service_name)
                service = None
                # my service is gone, forget my id
                self.service_id = ''
            elif e.response.status_code == 500:
                self.log.info("Service '%s' is on unhealthy node", self.service_name)
                service = None
                # my service is unhealthy, forget my id
                self.service_id = ''
            else:
                raise
        return service

    @gen.coroutine
    def get_task(self):
        self.log.debug("Getting task of service '%s'", self.service_name)
        if self.get_service() is None:
            return None
        try:
            tasks = yield self.docker('tasks', filters={'service': self.service_name, 'desired-state': 'running'})
            if len(tasks) == 0:
                return None
            elif len(tasks) > 1:
                # self.log.critical(pformat(tasks))
                raise RuntimeError("Found more than one running notebook task for service '{}'".format(self.service_name))
            task = tasks[0]
            # self.log.critical(pformat(task))
        except APIError as e:
            if e.response.status_code == 404:
                self.log.info("Task for service '%s' is gone", self.service_name)
                task = None
            else:
                raise

        return task


    @property
    def _container_spec_keys(self):
        return [s.strip() for s in "image, command, args, hostname, env, workdir, user, labels, mounts, "
                                   "stop_grace_period, secrets, tty, groups, open_stdin, read_only, stop_signal, "
                                   "healthcheck, hosts, dns_config, configs, privileges".split(',')]

    @property
    def _resource_spec_keys(self):
        return [s.strip() for s in "cpu_limit, mem_limit, cpu_reservation, mem_reservation".split(',')]

    @property
    def _task_spec_keys(self):
        return ["networks"]

    @property
    def _endpoint_spec_keys(self):
        return ["ports"]

    @gen.coroutine
    def start(self, image=None, extra_create_kwargs=None,
              extra_start_kwargs=None, extra_host_config=None):
        """Start the single-user server in a docker service. You can override
        the default parameters passed to `create_service` through the
        `extra_create_kwargs` dictionary and passed to `start` through the
        `extra_start_kwargs` dictionary.  You can also override the
        'host_config' parameter passed to `create_service` through the
        `extra_host_config` dictionary.

        Per-instance `extra_create_kwargs`, `extra_start_kwargs`, and
        `extra_host_config` take precedence over their global counterparts.

        """
        service = yield self.get_service()
        if service and self.remove_services:
            self.log.warning(
                "Removing service that should have been cleaned up: %s (id: %s)",
                self.service_name, self.service_id[:7])
            # remove the service, as well as any associated volumes
            yield self.docker('remove_service', self.service_id)
            service = None

        if service is None:
            image = image or self.image
            cmd = None
            if self._user_set_cmd:
                cmd = self.cmd

            # build the dictionary of keyword arguments for create_service
            create_kwargs = dict(
                image=image,
                env=self.get_env(),
                mounts=self.mounts,
                name=self.service_name,
                args=self.get_args(),
                mem_limit=self.mem_limit,
                mem_reservation=self.mem_guarantee,
                cpu_limit=int(self.cpu_limit * 1e9) if self.cpu_limit else None,
                cpu_reservation=int(self.cpu_guarantee * 1e9) if self.cpu_guarantee else None,
                networks=[self.network_name] if self.network_name else [],
                # ports={self.port: (None, 'tcp')},
            )

            if cmd:
                create_kwargs['command'] = cmd


            create_kwargs.update(self.extra_create_kwargs)
            if extra_create_kwargs:
                create_kwargs.update(extra_create_kwargs)

            # create the service
            self.log.warning(create_kwargs)

            container_spec = {k: v for k, v in create_kwargs.items() if k in self._container_spec_keys}
            container_spec = ContainerSpec(**container_spec)
            self.log.debug(container_spec)
            resource_spec = {k: v for k, v in create_kwargs.items() if k in self._resource_spec_keys}
            resource_spec = Resources(**resource_spec)
            self.log.debug(resource_spec)
            task_spec = {k: v for k, v in create_kwargs.items() if k in self._task_spec_keys}
            task_spec = TaskTemplate(container_spec=container_spec, resources=resource_spec, force_update=1, **task_spec)
            self.log.debug(task_spec)
            endpoint_spec = {k: v for k, v in create_kwargs.items() if k in self._endpoint_spec_keys}
            endpoint_spec = EndpointSpec(**endpoint_spec)
            self.log.debug(endpoint_spec)

            remaining_keys = set(create_kwargs.keys()) - set().union(self._container_spec_keys, self._resource_spec_keys, self._task_spec_keys, self._endpoint_spec_keys, {"name"})
            if remaining_keys:
                remaining_keys = {k: create_kwargs[k] for k in remaining_keys}
                self.log.critical("Unused configuration keys: {}".format(pformat(remaining_keys)))

            resp = yield self.docker('create_service', task_template=task_spec, endpoint_spec=endpoint_spec, name=create_kwargs['name'])
            self.service_id = resp['ID']
            self.log.info(
                "Created service '%s' (id: %s) from image %s",
                self.service_name, self.service_id[:7], image)

        else:
            self.log.info(
                "Found existing service '%s' (id: %s)",
                self.service_name, self.service_id[:7])
            # Handle re-using API token.
            # Get the API token from the environment variables
            # of the running service:
            for line in service['Config']['Env']:
                if line.startswith(('JPY_API_TOKEN=', 'JUPYTERHUB_API_TOKEN=')):
                    self.api_token = line.split('=', 1)[1]
                    break

        # TODO: handle unpause
        self.log.info(
            "Starting service '%s' (id: %s)",
            self.service_name, self.service_id[:7])

        # build the dictionary of keyword arguments for start
        start_kwargs = {}
        start_kwargs.update(self.extra_start_kwargs)
        if extra_start_kwargs:
            start_kwargs.update(extra_start_kwargs)

        # start the service
        # TODO: service equivalent for this?
        # yield self.docker('start', self.service_id, **start_kwargs)

        ip, port = yield self.get_ip_and_port()
        if jupyterhub.version_info < (0, 7):
            # store on user for pre-jupyterhub-0.7:
            self.user.server.ip = ip
            self.user.server.port = port
        # jupyterhub 0.7 prefers returning ip, port:
        return (ip, port)

    @gen.coroutine
    def get_ip_and_port(self):
        """Queries Docker daemon for service's IP and port.

        If you are using network_mode=host, you will need to override
        this method as follows::

            @gen.coroutine
            def get_ip_and_port(self):
                return self.host_ip, self.port

        You will need to make sure host_ip and port
        are correct, which depends on the route to the service
        and the port it opens.
        """
        ip = self.service_name
        port = self.port

        return ip, port

    @gen.coroutine
    def stop(self, now=False):
        """Stop the service

        Consider using pause/unpause when docker-py adds support
        """
        self.log.info(
            "Stopping service %s (id: %s)",
            self.service_name, self.service_id[:7])
        yield self.docker('remove_service', self.service_id)

        # if self.remove_services:
        #     self.log.info(
        #         "Removing service %s (id: %s)",
        #         self.service_name, self.service_id[:7])
        #     # remove the service, as well as any associated volumes
        #     yield self.docker('remove_service', self.service_id, v=True)

        self.clear_state()
