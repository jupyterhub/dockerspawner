"""Tests for SwarmSpawner"""

from getpass import getuser
from unittest import mock

import pytest
from jupyterhub.tests.test_api import add_user, api_request
from jupyterhub.tests.mocking import public_url
from jupyterhub.tests.utils import async_requests
from jupyterhub.utils import url_path_join

from dockerspawner import SystemUserSpawner

pytestmark = pytest.mark.usefixtures("systemuserspawner")


@pytest.fixture
def systemuserspawner(app):
    """Configure JupyterHub to use DockerSpawner"""
    app.config.SwarmSpawner.prefix = "dockerspawner-test"
    with mock.patch.dict(
        app.tornado_settings, {"spawner_class": SystemUserSpawner}
    ):
        yield


@pytest.mark.gen_test
def test_start_stop(app):
    name = getuser()
    add_user(app.db, app, name=name)
    user = app.users[name]
    assert isinstance(user.spawner, SystemUserSpawner)
    token = user.new_api_token()
    # start the server
    r = yield api_request(app, "users", name, "server", method="post")
    while r.status_code == 202:
        # request again
        r = yield api_request(app, "users", name, "server", method="post")
    assert r.status_code == 201, r.text
    url = url_path_join(public_url(app, user), "api/status")
    r = yield async_requests.get(url, headers={"Authorization": "token %s" % token})
    assert r.url == url
    r.raise_for_status()
    print(r.text)
    assert "kernels" in r.json()
