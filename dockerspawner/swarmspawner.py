"""
A Spawner for JupyterHub that runs each user's server in a separate docker service
"""

from pprint import pformat
from textwrap import dedent

from docker.types import (
    ContainerSpec, TaskTemplate, Resources, EndpointSpec, Mount, DriverConfig
)
from docker.errors import APIError
from tornado import gen
from traitlets import Dict, Unicode, Bool, Int, Any, default, observe

from .dockerspawner import DockerSpawner
import jupyterhub


class SwarmSpawner(DockerSpawner):
    """A Spawner for JupyterHub that runs each user's server in a separate docker service"""

    object_type = "service"

    @property
    def service_id(self):
        """alias for object_id"""
        return self.object_id

    @property
    def service_name(self):
        """alias for object_name"""
        return self.object_name

    extra_resources_spec = Dict(
        config=True,
        help="""
        Keyword arguments to pass to the Resources spec
        """,
    )

    extra_container_spec = Dict(
        config=True,
        help="""
        Keyword arguments to pass to the ContainerSpec constructor
        """,
    )

    extra_task_spec = Dict(
        config=True,
        help="""
        Keyword arguments to pass to the TaskTemplate constructor
        """,
    )

    extra_endpoint_spec = Dict(
        config=True,
        help="""
        Keyword arguments to pass to the Endpoint constructor
        """,
    )

    volume_driver = Unicode(
        "",
        config=True,
        help=dedent(
            """
            Use this driver for mounting the notebook volumes.
            Note that this driver must support multiple hosts in order for it to work across the swarm.
            For a list of possible drivers, see https://docs.docker.com/engine/extend/legacy_plugins/#volume-plugins
            """
        ),
    )

    volume_driver_options = Dict(
        config=True,
        help=dedent(
            """
            Configuration options for the multi-host volume driver.
            """
        ),
    )

    @property
    def mount_driver_config(self):
        return DriverConfig(
            name=self.volume_driver, options=self.volume_driver_options or None
        )

    @property
    def mounts(self):
        if len(self.volume_binds):
            driver = self.mount_driver_config
            return [
                Mount(
                    target=vol["bind"],
                    source=host_loc,
                    type="bind",
                    read_only=vol["mode"] == "ro",
                    driver_config=driver,
                )
                for host_loc, vol in self.volume_binds.items()
            ]

        else:
            return []

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

    @gen.coroutine
    def start(self):
        """Start the single-user server in a docker service."""
        service = yield self.get_object()
        if service and self.remove:
            self.log.warning(
                "Removing service that should have been cleaned up: %s (id: %s)",
                self.service_name, self.service_id[:7])
            # remove the service, as well as any associated volumes
            yield self.docker('remove_service', self.service_id)
            service = None

        if service is None:
            cmd = None
            if self._user_set_cmd:
                cmd = self.cmd

            # build the dictionary of keyword arguments for create_service
            container_kwargs = dict(
                image=self.image,
                env=self.get_env(),
                args=self.get_args(),
                mounts=self.mounts,
            )
            if cmd:
                container_kwargs['command'] = cmd
            container_kwargs.update(self.extra_container_spec)
            container_spec = ContainerSpec(**container_kwargs)

            resources_kwargs = dict(
                mem_limit=self.mem_limit,
                mem_reservation=self.mem_guarantee,
                cpu_limit=int(self.cpu_limit * 1e9) if self.cpu_limit else None,
                cpu_reservation=int(self.cpu_guarantee * 1e9) if self.cpu_guarantee else None,
            )
            resources_kwargs.update(self.extra_resources_spec)
            resources_spec = Resources(**resources_kwargs)

            task_kwargs = dict(
                container_spec=container_spec,
                resources=resources_spec,
                networks=[self.network_name] if self.network_name else [],
            )
            task_kwargs.update(self.extra_task_spec)
            task_spec = TaskTemplate(**task_kwargs)

            endpoint_kwargs = {}
            endpoint_kwargs.update(self.extra_endpoint_spec)
            endpoint_spec = EndpointSpec(**endpoint_kwargs)

            create_kwargs = dict(
                task_template=task_spec,
                endpoint_spec=endpoint_spec,
                name=self.service_name,
            )
            create_kwargs.update(self.extra_create_kwargs)

            resp = yield self.docker('create_service', **create_kwargs)

            self.object_id = resp['Id']
            self.log.info(
                "Created service '%s' (id: %s) from image %s",
                self.service_name, self.service_id[:7], self.image)

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

        # if self.remove:
        #     self.log.info(
        #         "Removing service %s (id: %s)",
        #         self.service_name, self.service_id[:7])
        #     # remove the service, as well as any associated volumes
        #     yield self.docker('remove_service', self.service_id, v=True)

        self.clear_state()
