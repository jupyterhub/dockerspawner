"""pytest config for dockerspawner tests"""
import inspect
import json
import os
from textwrap import indent
from unittest import mock

import jupyterhub
import netifaces
import pytest
from pytest_jupyterhub.jupyterhub_spawners import hub_app
from docker import from_env as docker_from_env
from docker.errors import APIError
from jupyterhub import version_info as jh_version_info
from jupyterhub.tests.conftest import app as jupyterhub_app  # noqa: F401
from jupyterhub.tests.conftest import event_loop  # noqa: F401
from jupyterhub.tests.conftest import io_loop  # noqa: F401
from jupyterhub.tests.conftest import ssl_tmpdir  # noqa: F401
from jupyterhub.tests.mocking import MockHub

from dockerspawner import DockerSpawner, SwarmSpawner, SystemUserSpawner


# import base jupyterhub fixtures

# make Hub connectable from docker by default
# do this here because the `app` fixture has already loaded configuration


MockHub.hub_ip = "0.0.0.0"

if os.environ.get("HUB_CONNECT_IP"):
    MockHub.hub_connect_ip = os.environ["HUB_CONNECT_IP"]
else:
    # get docker interface explicitly by default
    # on GHA, the ip for hostname resolves to a 10.x
    # address that is not connectable from within containers
    # but the docker0 address is connectable
    docker_interfaces = sorted(
        iface for iface in netifaces.interfaces() if 'docker' in iface
    )
    if docker_interfaces:
        iface = docker_interfaces[0]
        print(f"Found docker interfaces: {docker_interfaces}, using {iface}")
        MockHub.hub_connect_ip = netifaces.ifaddresses(docker_interfaces[0])[
            netifaces.AF_INET
        ][0]['addr']


def pytest_collection_modifyitems(items):
    """This function is automatically run by pytest passing all collected test
    functions.

    We use it to add asyncio marker to all async tests and assert we don't use
    test functions that are async generators which wouldn't make sense.
    """
    for item in items:
        if inspect.iscoroutinefunction(item.obj):
            item.add_marker('asyncio')
        assert not inspect.isasyncgenfunction(item.obj)


""" 
@pytest.fixture
def app(jupyterhub_app):
    app = jupyterhub_app
    app.config.DockerSpawner.prefix = "dockerspawner-test"
    # If it's a prerelease e.g. (2, 0, 0, 'rc4', '') use full tag
    if len(jh_version_info) > 3 and jh_version_info[3]:
        tag = jupyterhub.__version__
        app.config.DockerSpawner.image = f"jupyterhub/singleuser:{tag}"
    return app
 """
 

@pytest.fixture
async def app(hub_app):
    config = {
        "Dockerspawner": {
            "prefix": "dockerspawner-test"
        }
    }

    if len(jh_version_info) > 3 and jh_version_info[3]:
        tag = jupyterhub.__version__
        config["Dockerspawner"]["image"] = f"jupyterhub/singleuser:{tag}"
    
    app = await hub_app(config=config)

    return app


@pytest.fixture
async def named_servers(app):
    with mock.patch.dict(
        app.tornado_settings,
        {"allow_named_servers": True, "named_server_limit_per_user": 2},
    ):
        yield


@pytest.fixture
async def dockerspawner_configured_app(app, named_servers):
    """Configure JupyterHub to use DockerSpawner"""
    # app.config.DockerSpawner.remove = True
    with mock.patch.dict(app.tornado_settings, {"spawner_class": DockerSpawner}):
        yield app


@pytest.fixture
async def swarmspawner_configured_app(app, named_servers):
    """Configure JupyterHub to use DockerSpawner"""
    with mock.patch.dict(
        app.tornado_settings, {"spawner_class": SwarmSpawner}
    ), mock.patch.dict(app.config.SwarmSpawner, {"network_name": "bridge"}):
        yield app


@pytest.fixture
async def systemuserspawner_configured_app(app, named_servers):
    """Configure JupyterHub to use DockerSpawner"""
    with mock.patch.dict(app.tornado_settings, {"spawner_class": SystemUserSpawner}):
        yield app


@pytest.fixture(autouse=True, scope="session")
def docker():
    """Fixture to return a connected docker client

    cleans up any containers we leave in docker
    """
    d = docker_from_env()
    try:
        yield d

    finally:
        # cleanup our containers
        for c in d.containers.list(all=True):
            if c.name.startswith("dockerspawner-test"):
                c.stop()
                c.remove()
        try:
            services = d.services.list()
        except APIError:
            # e.g. services not available
            return
        else:
            for s in services:
                if s.name.startswith("dockerspawner-test"):
                    s.remove()


# make sure reports are available during yield fixtures
# from pytest docs: https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def debug_docker(request, docker):
    """Debug docker state after tests"""
    yield
    if not hasattr(request.node, 'rep_call'):
        return
    if not request.node.rep_call.failed:
        return

    print("executing test failed", request.node.nodeid)
    containers = docker.containers.list(all=True)
    for c in containers:
        print(f"Container {c.name}: {c.status}")

    for c in containers:
        logs = indent(c.logs().decode('utf8', 'replace'), '  ')
        print(f"Container {c.name} logs:\n{logs}")

    for c in containers:
        container_info = json.dumps(
            docker.api.inspect_container(c.id),
            indent=2,
            sort_keys=True,
        )
        print(f"Container {c.name}: {container_info}")


_username_counter = 0


@pytest.fixture()
def username():
    global _username_counter
    _username_counter += 1
    return f"test-user-{_username_counter}"
