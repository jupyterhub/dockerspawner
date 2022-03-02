"""
A Spawner for JupyterHub that runs each user's server in a separate docker service
"""
import asyncio
from pprint import pformat
from textwrap import dedent

from docker.errors import APIError
from docker.types import ContainerSpec
from docker.types import DriverConfig
from docker.types import EndpointSpec
from docker.types import Mount
from docker.types import Placement
from docker.types import Resources
from docker.types import TaskTemplate
from traitlets import default
from traitlets import Dict
from traitlets import Unicode

from .dockerspawner import DockerSpawner


class SwarmSpawner(DockerSpawner):
    """A Spawner for JupyterHub that runs each user's server in a separate docker service"""

    object_type = "service"
    object_id_key = "ID"

    @default("pull_policy")
    def _default_pull_policy(self):
        # pre-pulling doesn't usually make sense on swarm
        # unless it's a single-node cluster, so skip it by efault
        return "skip"

    @property
    def service_id(self):
        """alias for object_id"""
        return self.object_id

    @property
    def service_name(self):
        """alias for object_name"""
        return self.object_name

    @default("network_name")
    def _default_network_name(self):
        # no default network for swarm
        # use internal networking by default
        return ""

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

    extra_placement_spec = Dict(
        config=True,
        help="""
        Keyword arguments to pass to the Placement constructor
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

    # container-removal cannot be disabled for services
    remove = True

    @property
    def mount_driver_config(self):
        if self.volume_driver:
            return DriverConfig(
                name=self.volume_driver, options=self.volume_driver_options or None
            )
        return None

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

    async def poll(self):
        """Check for my id in `docker ps`"""
        service = await self.get_task()
        if not service:
            self.log.warning("Service %s not found", self.service_name)
            return 0

        service_state = service["Status"]
        self.log.debug(
            "Service %s status: %s", self.service_id[:7], pformat(service_state)
        )

        if service_state["State"] in {"running", "starting", "pending", "preparing"}:
            return None

        else:
            return pformat(service_state)

    async def get_task(self):
        self.log.debug("Getting task of service '%s'", self.service_name)
        if await self.get_object() is None:
            return None

        try:
            tasks = await self.docker(
                "tasks",
                filters={"service": self.service_name, "desired-state": "running"},
            )
            if len(tasks) == 0:
                tasks = await self.docker(
                    "tasks",
                    filters={"service": self.service_name},
                )
                if len(tasks) == 0:
                    return None

            elif len(tasks) > 1:
                raise RuntimeError(
                    "Found more than one running notebook task for service '{}'".format(
                        self.service_name
                    )
                )

            task = tasks[0]
        except APIError as e:
            if e.response.status_code == 404:
                self.log.info("Task for service '%s' is gone", self.service_name)
                task = None
            else:
                raise

        return task

    async def create_object(self):
        """Start the single-user server in a docker service."""
        container_kwargs = dict(
            image=self.image,
            env=self.get_env(),
            args=(await self.get_command()),
            mounts=self.mounts,
        )
        container_kwargs.update(self.extra_container_spec)
        container_spec = ContainerSpec(**container_kwargs)

        resources_kwargs = dict(
            mem_limit=self.mem_limit,
            mem_reservation=self.mem_guarantee,
            cpu_limit=int(self.cpu_limit * 1e9) if self.cpu_limit else None,
            cpu_reservation=int(self.cpu_guarantee * 1e9)
            if self.cpu_guarantee
            else None,
        )
        resources_kwargs.update(self.extra_resources_spec)
        resources_spec = Resources(**resources_kwargs)

        placement_kwargs = dict(
            constraints=None,
            preferences=None,
            platforms=None,
        )
        placement_kwargs.update(self.extra_placement_spec)
        placement_spec = Placement(**placement_kwargs)

        task_kwargs = dict(
            container_spec=container_spec,
            resources=resources_spec,
            networks=[self.network_name] if self.network_name else [],
            placement=placement_spec,
        )
        task_kwargs.update(self.extra_task_spec)
        task_spec = TaskTemplate(**task_kwargs)

        endpoint_kwargs = {}
        if not self.use_internal_ip:
            endpoint_kwargs["ports"] = {None: (self.port, "tcp")}
        endpoint_kwargs.update(self.extra_endpoint_spec)
        endpoint_spec = EndpointSpec(**endpoint_kwargs)

        create_kwargs = dict(
            task_template=task_spec, endpoint_spec=endpoint_spec, name=self.service_name
        )
        create_kwargs.update(self.extra_create_kwargs)

        service = await self.docker("create_service", **create_kwargs)

        while True:
            tasks = await self.docker(
                "tasks",
                filters={"service": self.service_name},
            )
            if len(tasks) > 0:
                break
            await asyncio.sleep(1)

        return service

    @property
    def internal_hostname(self):
        return self.service_name

    async def remove_object(self):
        self.log.info("Removing %s %s", self.object_type, self.object_id)
        # remove the container, as well as any associated volumes
        await self.docker("remove_" + self.object_type, self.object_id)

    async def start_object(self):
        """Not actually starting anything

        but use this to wait for the container to be running.

        Spawner.start shouldn't return until the Spawner
        believes a server is *running* somewhere,
        not just requested.
        """

        dt = 1.0

        while True:
            service = await self.get_task()
            if not service:
                raise RuntimeError("Service %s not found" % self.service_name)

            status = service["Status"]
            state = status["State"].lower()
            self.log.debug("Service %s state: %s", self.service_id[:7], state)
            if state in {
                "new",
                "assigned",
                "accepted",
                "starting",
                "pending",
                "preparing",
                "ready",
                "rejected",
            }:
                # not ready yet, wait before checking again
                await asyncio.sleep(dt)
                # exponential backoff
                dt = min(dt * 1.5, 11)
            else:
                break
        if state != "running":
            raise RuntimeError(
                "Service %s not running: %s" % (self.service_name, pformat(status))
            )

    async def stop_object(self):
        """Nothing to do here

        There is no separate stop action for services
        """
        pass

    async def get_ip_and_port(self):
        """Queries Docker daemon for service's IP and port.

        If you are using network_mode=host, you will need to override
        this method as follows::

            async def get_ip_and_port(self):
                return self.host_ip, self.port

        You will need to make sure host_ip and port
        are correct, which depends on the route to the service
        and the port it opens.
        """
        if self.use_internal_hostname or self.use_internal_ip:
            ip = self.service_name
            port = self.port
        else:
            # discover published ip, port
            ip = self.host_ip
            service = await self.get_object()
            for port_config in service["Endpoint"]["Ports"]:
                if port_config.get("TargetPort") == self.port:
                    port = port_config["PublishedPort"]
                    break

            else:
                self.log.error(
                    "Couldn't find PublishedPort for %s in %s",
                    self.port,
                    service["Endpoint"]["Ports"],
                )
                raise RuntimeError(
                    "Couldn't identify port for service %s", self.service_name
                )

        return ip, port
