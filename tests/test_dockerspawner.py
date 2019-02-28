"""Tests for DockerSpawner class"""

import json

import docker
import pytest
from jupyterhub.tests.test_api import add_user, api_request
from jupyterhub.tests.mocking import public_url
from jupyterhub.tests.utils import async_requests
from jupyterhub.utils import url_path_join
from tornado import gen

from dockerspawner import DockerSpawner

pytestmark = pytest.mark.usefixtures("dockerspawner")


@pytest.mark.gen_test(timeout=90)
def test_start_stop(app):
    name = "has@"
    add_user(app.db, app, name=name)
    user = app.users[name]
    assert isinstance(user.spawner, DockerSpawner)
    token = user.new_api_token()
    # start the server
    r = yield api_request(app, "users", name, "server", method="post")
    while r.status_code == 202:
        # request again
        r = yield api_request(app, "users", name, "server", method="post")
        yield gen.sleep(0.1)
    assert r.status_code == 201, r.text
    url = url_path_join(public_url(app, user), "api/status")
    r = yield async_requests.get(url, headers={"Authorization": "token %s" % token})
    assert r.url == url
    r.raise_for_status()
    print(r.text)
    assert "kernels" in r.json()


@pytest.mark.gen_test(timeout=90)
@pytest.mark.parametrize("image", ["0.8", "0.9", "nomatch"])
def test_image_whitelist(app, image):
    name = "checker"
    add_user(app.db, app, name=name)
    user = app.users[name]
    assert isinstance(user.spawner, DockerSpawner)
    user.spawner.remove_containers = True
    user.spawner.image_whitelist = {
        "0.9": "jupyterhub/singleuser:0.9",
        "0.8": "jupyterhub/singleuser:0.8",
    }
    token = user.new_api_token()
    # start the server
    r = yield api_request(
        app, "users", name, "server", method="post", data=json.dumps({"image": image})
    )
    if image not in user.spawner.image_whitelist:
        with pytest.raises(Exception):
            r.raise_for_status()
        return
    while r.status_code == 202:
        # request again
        r = yield api_request(app, "users", name, "server", method="post")
        yield gen.sleep(0.1)
    assert r.status_code == 201, r.text
    url = url_path_join(public_url(app, user), "api/status")
    r = yield async_requests.get(url, headers={"Authorization": "token %s" % token})
    r.raise_for_status()
    assert r.headers['x-jupyterhub-version'].startswith(image)
    r = yield api_request(
        app, "users", name, "server", method="delete",
    )
    r.raise_for_status()


@pytest.mark.gen_test(timeout=90)
def test_image_pull_policy(app):
    name = "gumby"
    add_user(app.db, app, name=name)
    user = app.users[name]
    assert isinstance(user.spawner, DockerSpawner)
    spawner = user.spawners[""]
    spawner.image = "jupyterhub/doesntexist:nosuchtag"
    with pytest.raises(docker.errors.NotFound):
        spawner.image_pull_policy = "never"
        yield spawner.pull_image(spawner.image)

    repo = "busybox"
    tag = "1.29.1"  # a version that's definitely not latest
    # ensure image isn't present
    try:
        yield spawner.docker("remove_image", "{}:{}".format(repo, tag))
    except docker.errors.ImageNotFound:
        pass

    spawner.pull_policy = "ifnotpresent"
    image = "{}:{}".format(repo, tag)
    # should trigger a pull
    yield spawner.pull_image(image)
    # verify that the image exists now
    old_image_info = yield spawner.docker("inspect_image", image)
    print(old_image_info)

    # now tag busybox:latest as our current version
    # which is not latest!
    yield spawner.docker("tag", image, repo)

    image = repo  # implicit :latest
    spawner.pull_policy = "ifnotpresent"
    # check with ifnotpresent shouldn't pull
    yield spawner.pull_image(image)
    image_info = yield spawner.docker("inspect_image", repo)
    assert image_info["Id"] == old_image_info["Id"]

    # run again with Always,
    # should trigger a pull even though the image is present
    spawner.pull_policy = "always"
    spawner.pull_image(image)
    image_info = yield spawner.docker("inspect_image", repo)
    assert image_info["Id"] != old_image_info["Id"]

    # run again with never, make sure it's still happy
    spawner.pull_policy = "never"
    spawner.pull_image(image)
