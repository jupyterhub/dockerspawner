"""Tests for DockerSpawner class"""
import asyncio
import json
import logging
import os
import string
from unittest import mock

import docker
import pytest
import traitlets
from escapism import escape
from jupyterhub.tests.mocking import public_url
from jupyterhub.tests.test_api import add_user, api_request
from jupyterhub.utils import url_path_join
from tornado.httpclient import AsyncHTTPClient

from dockerspawner import DockerSpawner


def test_name_collision(dockerspawner_configured_app):
    app = dockerspawner_configured_app
    has_hyphen = "user--foo"
    add_user(app.db, app, name=has_hyphen)
    user = app.users[has_hyphen]
    spawner1 = user.spawners[""]
    assert isinstance(spawner1, DockerSpawner)
    assert spawner1.object_name == "{}-{}".format(
        spawner1.prefix, has_hyphen.replace("-", "-2d")
    )

    part1, part2 = ["user", "foo"]
    add_user(app.db, app, name=part1)
    user2 = app.users[part1]
    spawner2 = user2.spawners[part2]
    assert spawner1.object_name != spawner2.object_name


@pytest.mark.parametrize("remove", (True, False))
async def test_start_stop(dockerspawner_configured_app, remove):
    app = dockerspawner_configured_app
    name = "has@"
    add_user(app.db, app, name=name)
    user = app.users[name]
    server_name = 'also-has@'
    spawner = user.spawners[server_name]
    assert isinstance(spawner, DockerSpawner)
    spawner.remove = remove
    token = user.new_api_token()
    # start the server
    r = await api_request(app, "users", name, "servers", server_name, method="post")
    pending = r.status_code == 202
    while pending:
        # request again
        await asyncio.sleep(2)
        r = await api_request(app, "users", name)
        user_info = r.json()
        pending = user_info["servers"][server_name]["pending"]
    assert r.status_code in {201, 200}, r.text

    url = url_path_join(public_url(app, user), server_name, "api/status")
    resp = await AsyncHTTPClient().fetch(
        url, headers={"Authorization": "token %s" % token}
    )
    assert resp.effective_url == url
    resp.rethrow()
    assert "kernels" in resp.body.decode("utf-8")

    # stop the server
    r = await api_request(app, "users", name, "servers", server_name, method="delete")
    pending = r.status_code == 202
    while pending:
        # request again
        await asyncio.sleep(2)
        r = await api_request(app, "users", name)
        user_info = r.json()
        pending = user_info["servers"][server_name]["pending"]
    assert r.status_code in {204, 200}, r.text
    state = spawner.get_state()
    if remove:
        assert state == {}
    else:
        assert sorted(state) == ["object_id", "object_name"]


def allowed_images_callable(*_):
    return ["jupyterhub/singleuser:1.0", "jupyterhub/singleuser:1.1"]


@pytest.mark.parametrize(
    "allowed_images, image",
    [
        (
            {
                "1.0": "jupyterhub/singleuser:1.0",
                "1.1": "jupyterhub/singleuser:1.1",
            },
            "1.0",
        ),
        (["jupyterhub/singleuser:1.0", "jupyterhub/singleuser:1.1.0"], "1.1.0"),
        (allowed_images_callable, "1.0"),
    ],
)
async def test_allowed_image(dockerspawner_configured_app, allowed_images, image):
    app = dockerspawner_configured_app
    name = "checker"
    add_user(app.db, app, name=name)
    user = app.users[name]
    assert isinstance(user.spawner, DockerSpawner)
    user.spawner.remove_containers = True
    user.spawner.allowed_images = allowed_images
    token = user.new_api_token()
    # start the server
    r = await api_request(
        app,
        "users",
        name,
        "server",
        method="post",
        data=json.dumps({"image": image}),
    )

    if image not in user.spawner._get_allowed_images():
        with pytest.raises(Exception):
            r.raise_for_status()
        return
    pending = r.status_code == 202
    while pending:
        # request again
        await asyncio.sleep(2)
        r = await api_request(app, "users", name)
        user_info = r.json()
        pending = user_info["servers"][""]["pending"]

    url = url_path_join(public_url(app, user), "api/status")
    resp = await AsyncHTTPClient().fetch(
        url, headers={"Authorization": "token %s" % token}
    )
    assert resp.effective_url == url
    resp.rethrow()

    assert resp.headers['x-jupyterhub-version'].startswith(image)
    r = await api_request(
        app,
        "users",
        name,
        "server",
        method="delete",
    )
    r.raise_for_status()


@pytest.mark.xfail(
    "podman.sock" in os.getenv("DOCKER_HOST", ""), reason="Fails with Podman"
)
async def test_image_pull_policy(dockerspawner_configured_app):
    app = dockerspawner_configured_app
    name = "gumby"
    add_user(app.db, app, name=name)
    user = app.users[name]
    assert isinstance(user.spawner, DockerSpawner)
    spawner = user.spawners[""]
    spawner.image = "jupyterhub/doesntexist:nosuchtag"
    with pytest.raises(docker.errors.NotFound):
        spawner.image_pull_policy = "never"
        await spawner.pull_image(spawner.image)

    repo = "busybox"
    tag = "1.29.1"  # a version that's definitely not latest
    # ensure image isn't present
    try:
        await asyncio.wrap_future(spawner.docker("remove_image", f"{repo}:{tag}"))
    except docker.errors.ImageNotFound:
        pass

    spawner.pull_policy = "ifnotpresent"
    image = f"{repo}:{tag}"
    # should trigger a pull
    await spawner.pull_image(image)
    # verify that the image exists now
    old_image_info = await asyncio.wrap_future(spawner.docker("inspect_image", image))
    print(old_image_info)

    # now tag busybox:latest as our current version
    # which is not latest!
    await asyncio.wrap_future(spawner.docker("tag", image, repo))

    image = repo  # implicit :latest
    spawner.pull_policy = "ifnotpresent"
    # check with ifnotpresent shouldn't pull
    await spawner.pull_image(image)
    image_info = await asyncio.wrap_future(spawner.docker("inspect_image", repo))
    assert image_info["Id"] == old_image_info["Id"]

    # run again with Always,
    # should trigger a pull even though the image is present
    spawner.pull_policy = "always"
    await spawner.pull_image(image)
    image_info = await asyncio.wrap_future(spawner.docker("inspect_image", repo))
    assert image_info["Id"] != old_image_info["Id"]

    # run again with never, make sure it's still happy
    spawner.pull_policy = "never"
    await spawner.pull_image(image)


async def test_post_start(dockerspawner_configured_app, caplog):
    app = dockerspawner_configured_app
    name = "post-start"
    add_user(app.db, app, name=name)
    user = app.users[name]
    spawner = user.spawners['']
    log_name = "dockerspawner"
    spawner.log = logging.getLogger(log_name)
    spawner.remove = True

    # mock out ip and port, no need for it
    async def mock_ip_port():
        return ("127.0.0.1", 1234)

    spawner.get_ip_and_port = mock_ip_port

    spawner.image = "busybox:1.29.1"
    spawner.cmd = ["sh", "-c", "sleep 300"]
    spawner.post_start_cmd = "ls /"

    # verify that it's called during startup
    finished_future = asyncio.Future()
    finished_future.set_result(None)
    mock_post_start = mock.Mock(return_value=finished_future)
    with mock.patch.object(spawner, 'post_start_exec', mock_post_start):
        await spawner.start()
    mock_post_start.assert_called_once()

    # verify log capture for 3 combinations:
    # - success
    # - failure
    # - no such command (different failure)

    for cmd, expected_stdout, expected_stderr in [
        ("true", False, False),
        ("ls /", True, False),
        ("ls /nosuchfile", False, True),
        ("nosuchcommand", False, True),
        ("echo", False, False),
    ]:
        spawner.post_start_cmd = cmd
        idx = len(caplog.records)
        with caplog.at_level(logging.DEBUG, log_name):
            await spawner.post_start_exec()
        logged = "\n".join(
            f"{rec.levelname}: {rec.message}" for rec in caplog.records[idx:]
        )
        if expected_stdout:
            assert "DEBUG: post_start stdout" in logged
        else:
            assert "post_start stdout" not in logged
        if expected_stderr:
            assert "WARNING: post_start stderr" in logged
        else:
            assert "post_start stderr" not in logged

    await spawner.stop()


@pytest.mark.skipif(
    traitlets.__version__ < '5.0', reason="One test fails on traitlets < 5.0. See #420."
)
@pytest.mark.parametrize(
    "mem_limit, expected",
    [
        ("1G", 1024**3),
        (1_000_000, 1_000_000),
        (None, None),
        (lambda spawner: None, None),
        (lambda spawner: "2G", 2 * 1024**3),
        (lambda spawner: 1_000_000, 1_000_000),
    ],
)
def test_mem_limit(mem_limit, expected):
    s = DockerSpawner(mem_limit=mem_limit)
    assert s.mem_limit == expected


@pytest.mark.parametrize(
    "cpu_limit, expected",
    [
        (1, 1),
        (None, None),
        (1.5, 1.5),
        (lambda spawner: None, None),
        (lambda spawner: 2, 2),
        (lambda spawner: 1.25, 1.25),
    ],
)
async def test_cpu_limit(dockerspawner_configured_app, cpu_limit, expected, username):
    app = dockerspawner_configured_app
    app.config.DockerSpawner.cpu_limit = cpu_limit
    add_user(app.db, app, name=username)
    user = app.users[username]
    s = user.spawners[""]
    assert s.cpu_limit == expected
    original_docker = s.docker

    async def mock_docker(cmd, *args, **kwargs):
        if cmd == "create_container":
            return args, kwargs
        else:
            return await original_docker(cmd, *args, **kwargs)

    with mock.patch.object(s, 'docker', new=mock_docker):
        args, kwargs = await s.create_object()

    print(kwargs)
    host_config = kwargs['host_config']
    if expected is not None:
        assert host_config['CpuPeriod'] == 100_000
        assert host_config['CpuQuota'] == int(expected * 100_000)
    else:
        assert 'CpuPeriod' not in host_config
        assert 'CpuQuota' not in host_config


@mock.patch.dict(os.environ, {"DOCKER_HOST": "tcp://127.0.0.2"}, clear=True)
def test_default_host_ip_reads_env_var():
    spawner = DockerSpawner()
    assert spawner._default_host_ip() == "127.0.0.2"


def test_default_options_form():
    spawner = DockerSpawner()
    spawner.allowed_images = {"1.0": "jupyterhub/singleuser:1.0"}
    assert spawner._default_options_form() == ''
    spawner.allowed_images["1.1"] = "jupyterhub/singleuser:1.1"
    assert (
        spawner._default_options_form()
        == """
        <label for="image">Select an image:</label>
        <select class="form-control" name="image" required autofocus>
        ['<option value="1.0" >1.0</option>', '<option value="1.1" >1.1</option>']
        </select>
        """
    )


def test_options_from_form():
    spawner = DockerSpawner()
    formdata = {'image': ['1.0', '1.1']}
    assert spawner.options_from_form(formdata) == {'image': '1.0'}


@pytest.mark.parametrize("escape_type", ("legacy", escape))
def test_validate_escape(escape_type):
    spawner = DockerSpawner()
    spawner.escape = escape_type
    with pytest.raises(Exception):
        spawner.escape = ""


def test_legacy_escape(dockerspawner_configured_app):
    app = dockerspawner_configured_app
    name = "cont@iner"
    add_user(app.db, app, name=name)
    user = app.users[name]
    server_name = 'cont@iner_server'
    spawner = user.spawners[server_name]
    assert isinstance(spawner, DockerSpawner)
    container_name_template = spawner.name_template
    container_name = container_name_template.format(
        prefix="jupyter", username=name, servername=server_name
    )
    safe_chars = set(string.ascii_letters + string.digits + "-")
    assert spawner._legacy_escape(container_name) == escape(
        container_name, safe_chars, escape_char='_'
    )
