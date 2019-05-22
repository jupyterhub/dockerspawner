import os
import time
from subprocess import Popen, check_call
from urllib.parse import urlparse

import docker
import pytest
import requests

here = os.path.dirname(__file__)
hub_url = 'http://127.0.0.1:8000'


@pytest.fixture(scope='session')
def compose_build():
    check_call(['docker-compose', 'build'], cwd=here)


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


@pytest.fixture(scope='session')
def compose_up(volumes_and_networks, compose_build):
    p = Popen(['docker-compose', 'up'], cwd=here)
    for i in range(60):
        try:
            r = requests.get(hub_url + '/hub/')
            r.raise_for_status()
        except Exception:
            time.sleep(1)
            if p.poll() is not None:
                raise RuntimeError("`docker-compose up` failed")
        else:
            break
    else:
        raise TimeoutError("hub never showed up at %s" % hub_url)

    try:
        yield
    finally:
        p.terminate()
        check_call(['docker-compose', 'rm', '-s', '-f'], cwd=here)


def test_internal_ssl(compose_up):
    s = requests.Session()
    r = s.post(hub_url + '/hub/login', data={'username': 'fake', 'password': 'ok'})
    r.raise_for_status()
    while "pending" in r.url:
        time.sleep(0.1)
        r = s.get(r.url)
        r.raise_for_status()
    assert urlparse(r.url).path == '/user/fake/tree'
