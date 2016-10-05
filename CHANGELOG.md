# Changes in DockerSpawner

For detailed changes from the prior release, click on the version number, and
its link will bring up a GitHub listing of changes. Use `git log` on the
command line for details.

## [Unreleased]

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


[Unreleased]: https://github.com/jupyterhub/dockerspawner/compare/0.5.0...HEAD
[0.5]: https://github.com/jupyterhub/dockerspawner/compare/0.4.0...0.5.0
[0.4]: https://github.com/jupyterhub/dockerspawner/compare/0.3.0...0.4.0
[0.3]: https://github.com/jupyterhub/dockerspawner/compare/0.2.0...0.3.0
[0.2]: https://github.com/jupyterhub/dockerspawner/compare/0.1.0...0.2.0