# DockerSpawner

[![GitHub Workflow Status - Test](https://img.shields.io/github/workflow/status/jupyterhub/dockerspawner/Tests?logo=github&label=tests)](https://github.com/jupyterhub/dockerspawner/actions)
[![Latest PyPI version](https://img.shields.io/pypi/v/dockerspawner?logo=pypi)](https://pypi.org/project/dockerspawner/)
[![Documentation build status](https://img.shields.io/readthedocs/jupyterhub?logo=read-the-docs)](https://jupyterhub-dockerspawner.readthedocs.org/en/latest/)
[![GitHub](https://img.shields.io/badge/issue_tracking-github-blue?logo=github)](https://github.com/jupyterhub/dockerspawner/issues)
[![Discourse](https://img.shields.io/badge/help_forum-discourse-blue?logo=discourse)](https://discourse.jupyter.org/c/jupyterhub)
[![Gitter](https://img.shields.io/badge/social_chat-gitter-blue?logo=gitter)](https://gitter.im/jupyterhub/jupyterhub)

The **dockerspawner** (also known as JupyterHub Docker Spawner), enables
[JupyterHub](https://github.com/jupyterhub/jupyterhub) to spawn single user
notebook servers in [Docker containers](https://www.docker.com/resources/what-container).

There are three basic types of spawners available for dockerspawner:

- DockerSpawner: takes an authenticated user and spawns a notebook server
  in a Docker container for the user.
- SwarmSpawner: launches single user notebook servers as Docker Swarm mode
  services.
- SystemUserSpawner: spawns single user notebook servers
  that correspond to system users.

See the [DockerSpawner documentation](https://jupyterhub-dockerspawner.readthedocs.org/en/latest/)
for more information about features and usage.

## Prerequisites

JupyterHub 0.7 or above is required, which also means Python 3.3 or above.

## Installation

Install dockerspawner to the system:

```bash
pip install dockerspawner
```

## Contributing

If you would like to contribute to the project (:heart:), please read our
[contributor documentation](http://jupyterhub-dockerspawner/en/latest/contributing.html)
and the [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

We use a shared copyright model that enables all contributors to maintain the
copyright on their contributions.

All code is licensed under the terms of the revised BSD license.

## Getting help

We encourage you to ask questions on the [Discourse community forum](https://discourse.jupyter.org/),
or [Gitter](https://gitter.im/jupyterhub/jupyterhub).

## Resources

### Dockerspawner and JupyterHub

- [Reporting Issues](https://github.com/jupyterhub/dockerspawner/issues)
- JupyterHub tutorial | [Repo](https://github.com/jupyterhub/jupyterhub-tutorial)
  | [Tutorial documentation](http://jupyterhub-tutorial.readthedocs.io/en/latest/)
- [Documentation for JupyterHub](http://jupyterhub.readthedocs.io/en/latest/) | [PDF (latest)](https://media.readthedocs.org/pdf/jupyterhub/latest/jupyterhub.pdf) | [PDF (stable)](https://media.readthedocs.org/pdf/jupyterhub/stable/jupyterhub.pdf)
- [Documentation for JupyterHub's REST API](http://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/jupyterhub/HEAD/docs/rest-api.yml#/default)

### Project Jupyter

- [Documentation for Project Jupyter](http://jupyter.readthedocs.io/en/latest/index.html) | [PDF](https://media.readthedocs.org/pdf/jupyter/latest/jupyter.pdf)
- [Project Jupyter website](https://jupyter.org)
