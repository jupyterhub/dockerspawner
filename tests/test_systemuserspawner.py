"""Tests for SwarmSpawner"""

from getpass import getuser

from jupyterhub.tests.mocking import public_url
from jupyterhub.tests.test_api import add_user, api_request
from jupyterhub.utils import url_path_join
from tornado.httpclient import AsyncHTTPClient

from dockerspawner import SystemUserSpawner


async def test_start_stop(systemuserspawner_configured_app):
    app = systemuserspawner_configured_app
    name = getuser()
    add_user(app.db, app, name=name)
    user = app.users[name]
    assert isinstance(user.spawner, SystemUserSpawner)
    token = user.new_api_token()
    # start the server
    r = await api_request(app, "users", name, "server", method="post")
    while r.status_code == 202:
        # request again
        r = await api_request(app, "users", name, "server", method="post")
    assert r.status_code == 201, r.text

    url = url_path_join(public_url(app, user), "api/status")
    resp = await AsyncHTTPClient().fetch(
        url, headers={"Authorization": "token %s" % token}
    )
    assert resp.effective_url == url
    resp.rethrow()
    assert "kernels" in resp.body.decode("utf-8")
