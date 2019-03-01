# Changes in DockerSpawner

For detailed changes from the prior release, click on the version number, and
its link will bring up a GitHub listing of changes. Use `git log` on the
command line for details.

## [Unreleased]

## 0.11

### [0.11.0] - 2019-03-01

#### New features:

- Support selecting docker spawner via JupyterHub 1.0's entrypoints:

  ```python
  c.JupyterHub.spawner_class = 'docker' # or 'docker-swarm' or 'docker-system-user'
  ```
- Support total internal SSL encryption with JupyterHub 1.0
- Add new `DockerSpawner.pull_policy` to configure pulling of images.
  Values are inspired by Kubernetes, and case-insensitive. Can be any of
  "IfNotPresent" (new default), "Always", and "Never" (pre-0.11 behavior).
  Now the image will be pulled by default if it is not present.
- Add `image_whitelist` configuration which, if set, defines a default options
  form for users to pick the desired image.
  `image_whitelist` is a dict of `{'descriptive key': 'image:tag'}`.
- Add `SwarmSpawner.extra_placement_spec` configuration for setting service placement

#### Fixes:

- Slow startup in SwarmSpawner could be treated as failures.


## 0.10

### [0.10.0] - 2018-09-03

- Add `dockerspawner.SwarmSpawner` for spawning with Docker Swarm
- Removed deprecated `extra_start_kwargs`
- `host_ip` is configurable
- Added `container_name_template` configuration for custom container naming

## 0.9

### [0.9.1] - 2017-08-23

- Fix typo which would cause using the deprecated `.hub_ip_connect` configuration
  with JupyterHub 0.8 to crash instead of warn in 0.9.0.

### [0.9.0] - 2017-08-20

0.9 cleans up some configuration and improves support for the transition from JupyterHub 0.8 to 0.9.
It also reduces some of the special arguments and env handling,
allowing for more consistency with other Spawners,
and fewer assumptions about the image that will be used by the Spawner.

The following is a minimal Dockerfile that works with DockerSpawner 0.9 and JupyterHub 0.7.2:

```Dockerfile
FROM python:3.6
RUN pip install \
    jupyterhub==0.8.0 \
    'notebook==5.0.0'

# Don't want to run as root!
RUN useradd -m jovyan
ENV HOME=/home/jovyan
WORKDIR $HOME
USER jovyan

CMD ["jupyterhub-singleuser"]
```

In particular:

- any image with the correct version of JupyterHub installed (it should match JupyterHub) should work with DockerSpawner.
- any image **based on one of the [jupyter/docker-stacks][]** should work with SystemUserSpawner.
  There is no longer any need for the `jupyterhub/systemuser` docker image.
- The jupyterhub/singleuser image is now built from the JupyterHub repo, not this one.
- `jupyterhub/systemuser` image is deprecated.
  `jupyterhub/systemuser` launches containers as root and relies on
  the `NB_UID` and `NB_GID` handling of `jupyter/docker-stacks` to setup the user.
- The default `jupyterhub/singleuser` image has tags for JupyterHub versions,
  to ensure image compatibility with JupyterHub.
  The default image is now `jupyterhub/singleuser:x.y`, where `x.y` is the major.minor version of
  the current JupyterHub instance,
  so DockerSpawner should work by default with JupyterHub 0.7 or 0.8
  without needing to specify the image.
- `Spawner.cmd` config is now supported, which can be used to override the CMD arg.
  By default, the image's CMD is used.
- `Spawner.get_args()` behavior is now properly inherited,
  and args are appended to the spawn command as in other Spawners.
- Arguments are now passed via `.get_args()` as in the base Spawner,
  rather than custom environment variables which user images had to support.
- `DockerSpawner.hub_ip_connect` is deprecated when running with JupyterHub 0.8.
  Use `JupyterHub.hub_connect_ip` instead, which is used by all Spawners.

Some configuration has been cleaned up to be clearer and more concise:

- `DockerSpawner.container_image` is deprecated in favor of `DockerSpawner.image`.
- `DockerSpawner.container_port` is deprecated in favor of existing `Spawner.port`.
- Inaccurately named `DockerSpawner.container_ip` is deprecated in favor of `DockerSpawner.host_ip`
  because it configures the host IP forwarded to the container.

[jupyter/docker-stacks]: https://github.com/jupyter/docker-stacks

## [0.8] - 2017-07-28

- experimental fixes for running on Windows
- added `DockerSpawner.client_kwargs` config to passthrough to the `docker.Client` constructor
- workaround bug where Docker can report ports as strings
- bump docker dependency to new `docker` package from `docker-py`


## [0.7] - 2017-03-14

- Only need to set `DockerSpawner.network_name` to run on a docker network,
  instead of setting `host_config`, `network_name`, and `use_internal_ip` separately.
- Set `mem_limit` on `host_config` for docker API 1.19
- Match start keyword args on SystemUserSpawner to DockerSpawner

## [0.6] - 2017-01-02

- Add `DockerSpawner.format_volume_name` for custom naming strategies for mounted volumes.
- Support `mem_limit` config introduced in JupyterHub 0.7.
- Support `will_resume` flag necessary for resuming containers with
  `DockerSpawner.remove_containers = False` and JupyterHub 0.7
  (requires JupyterHub 0.7.1).

## [0.5] - 2016-10-05

- return ip, port from `DockerSpawner.start`, for future-compatibility (setting ip, port directly is deprecated in JupyterHub 0.7).
- Support `{username}` in volume_mounts

## [0.4] - 2016-06-07

- get singleuser script from jupyterhub 0.6.1 (0.7 will require jupyterhub package to run singleuser script)
- `get_ip_and_port()` is a tornado coroutine, rather than an asyncio coroutine, for consistency with the rest of the code.
- more configuration for ports and mounts

## [0.3] - 2016-04-22

- Moved to jupyterhub org (`jupyterhub/singleuser`, `jupyterhub/systemuser` on Docker)
- Add `rebase-singleuser` tool for building new single-user images on top of different bases
- Base default docker images on `jupyter/scipy-notebook` from jupyter/docker-stacks
- Fix environment setup to use `get_env` instead of `_env_default` (Needed for JupyterHub 0.5)

## [0.2] - 2016-02-16

- Add `DockerSpawner.links`
- Use HostIp from docker port output
- Make user home string template configurable

## 0.1 - 2016-02-03

First release


[Unreleased]: https://github.com/jupyterhub/dockerspawner/compare/0.11.0...HEAD
[0.11.0]: https://github.com/jupyterhub/dockerspawner/compare/0.10.0...0.11.0
[0.10.0]: https://github.com/jupyterhub/dockerspawner/compare/0.9.1...0.10.0
[0.9.1]: https://github.com/jupyterhub/dockerspawner/compare/0.9.0...0.9.1
[0.9.0]: https://github.com/jupyterhub/dockerspawner/compare/0.8.0...0.9.0
[0.8]: https://github.com/jupyterhub/dockerspawner/compare/0.7.0...0.8.0
[0.7]: https://github.com/jupyterhub/dockerspawner/compare/0.6.0...0.7.0
[0.6]: https://github.com/jupyterhub/dockerspawner/compare/0.5.0...0.6.0
[0.5]: https://github.com/jupyterhub/dockerspawner/compare/0.4.0...0.5.0
[0.4]: https://github.com/jupyterhub/dockerspawner/compare/0.3.0...0.4.0
[0.3]: https://github.com/jupyterhub/dockerspawner/compare/0.2.0...0.3.0
[0.2]: https://github.com/jupyterhub/dockerspawner/compare/0.1.0...0.2.0
