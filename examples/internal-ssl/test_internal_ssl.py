import os
import sys
import time
from subprocess import Popen, check_call
from urllib.parse import urlparse

import docker
import pytest
import requests

here = os.path.dirname(__file__)
hub_url = 'http://localhost:8000'


@pytest.fixture(scope='session')
def compose_build():
    check_call(['docker', 'compose', 'build'], cwd=here)


@pytest.fixture(scope='session')
def volumes_and_networks():
    d = docker.from_env()
    volume_names = ('jupyterhub-ssl', 'jupyterhub-data')
    network_names = ('jupyterhub',)
    created = []
    for volume in volume_names:
        try:
            volume = d.volumes.get(volume)
        except docker.errors.NotFound:
            volume = d.volumes.create(volume)
        created.append(volume)
    for network in network_names:
        try:
            network = d.networks.get(network)
        except docker.errors.NotFound:
            network = d.networks.create(network)
        created.append(network)
    try:
        yield
    finally:
        for obj in created:
            try:
                obj.remove()
            except docker.errors.NotFound:
                pass
            except docker.errors.APIError as e:
                print(f"Error deleting {obj}: {e}", file=sys.stderr)


@pytest.fixture(scope='session')
def compose_up(volumes_and_networks, compose_build):
    p = Popen(['docker', 'compose', 'up'], cwd=here)
    for i in range(60):
        try:
            r = requests.get(hub_url + '/hub/')
            r.raise_for_status()
        except Exception:
            time.sleep(1)
            if p.poll() is not None:
                raise RuntimeError("`docker compose up` failed")
        else:
            break
    else:
        p.terminate()
        check_call(['docker', 'compose', 'rm', '-s', '-f'], cwd=here)
        raise TimeoutError("hub never showed up at %s" % hub_url)

    try:
        yield
    finally:
        p.terminate()
        check_call(['docker', 'compose', 'rm', '-s', '-f'], cwd=here)


def test_internal_ssl(compose_up):
    s = requests.Session()

    # acquire a _xsrf cookie to pass in the post request we are about to make
    r = s.get(hub_url + '/hub/login')
    r.raise_for_status()
    _xsrf_cookie = s.cookies.get("_xsrf", path="/hub/")
    assert _xsrf_cookie

    r = s.post(
        hub_url + '/hub/login',
        data={'username': 'fake', 'password': 'ok', '_xsrf': _xsrf_cookie},
    )
    r.raise_for_status()

    while "pending" in r.url:
        # request again
        time.sleep(2)
        r = s.get(r.url)
        r.raise_for_status()
    assert urlparse(r.url).path == '/user/fake/lab'
