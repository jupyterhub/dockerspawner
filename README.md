**[Prerequisites](#prerequisites)** |
**[Installation](#installation)** |
**[Configuration](#configuration)** |
**[Docker](#docker)** |
**[Contributing](#contributing)** |
**[License](#license)** |
**[Getting help](#getting-help)**


# DockerSpawner

** DockerSpawner enables [JupyterHub](https://github.com/jupyterhub/jupyterhub) 
to spawn single user notebook servers in Docker containers.


## Prerequisites

Python version 3.3 and above is required.

Clone the repo:

```bash

    git clone https://github.com/jupyterhub/dockerspawner.git
    cd dockerspawner
```

Install dependencies:

```bash
    pip install -r requirements.txt
```


## Installation

Install dockerspawner to the system:

```bash
    python setup.py install
```


## Configuration

### Choose a spawner

- DockerSpawner
- SystemUserSpawner

#### DockerSpawner

Tell JupyterHub to use DockerSpawner by adding the following line to 
your `jupyterhub_config.py`:

    c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

There is a complete example in [examples/oauth](examples/oauth) for
using GitHub OAuth to authenticate users, and spawn containers with docker.

#### SystemUserSpawner

If you want to spawn notebook servers for users that correspond to system users,
you can use the SystemUserSpawner instead. Add the following to your
`jupyterhub_config.py`:

    c.JupyterHub.spawner_class = 'dockerspawner.SystemUserSpawner'

The SystemUserSpawner will also need to know where the user home directories
are on the host. By default, it expects them to be in `/home/<username>`, but if
you want to change this, you'll need to further modify the
`jupyterhub_config.py`. For example, the following will look for a user's home
directory on the host system at `/volumes/user/<username>`:

    c.SystemUserSpawner.host_homedir_format_string = '/volumes/user/{username}'

For a full example of how `SystemUserSpawner` is used, see the
[compmodels-jupyterhub](https://github.com/jhamrick/compmodels-jupyterhub)
repository (this additionally runs the JupyterHub server within a docker
container, and authenticates users using GitHub OAuth).


### Using Docker Swarm

Both `DockerSpawner` and `SystemUserSpawner` are compatible with
[Docker Swarm](https://docs.docker.com/swarm/). Simply add to your
`jupyterhub_config.py` file:

```
c.DockerSpawner.container_ip = "0.0.0.0"
```

which will tell DockerSpawner/SystemUserSpawner to get the container IP address
and port number from `docker port`.


## Building the docker images

### Single user notebook server

Build the `jupyterhub/singleuser` container with:

    docker build -t jupyterhub/singleuser singleuser

or use `docker pull jupyterhub/singleuser` to download it from [Docker
Hub](https://registry.hub.docker.com/u/jupyterhub/singleuser/).

### System user notebook server

Or the `jupyterhub/systemuser` container with:

    docker build -t jupyterhub/systemuser systemuser

or use `docker pull jupyterhub/systemuser` to download it from [Docker
Hub](https://registry.hub.docker.com/u/jupyterhub/systemuser/).


## Contributing

If you would like to contribute to the project, please read our 
[contributor documentation](http://jupyter.readthedocs.io/en/latest/contributor/content-contributor.html)
and the [`CONTRIBUTING.md`](CONTRIBUTING.md).

For a **development install**, clone the [repository](https://github.com/jupyterhub/dockerspawner) 
and then install from source:

```bash
git clone https://github.com/jupyterhub/dockerspaawner
cd dockerspawner
pip3 install -r dev-requirements.txt -e .
```


## License

We use a shared copyright model that enables all contributors to maintain the
copyright on their contributions.

All code is licensed under the terms of the revised BSD license.


## Getting help

We encourage you to ask questions on the [mailing list](https://groups.google.com/forum/#!forum/jupyter),
and you may participate in development discussions or get live help on 
[Gitter](https://gitter.im/jupyterhub/jupyterhub).


## Resources

### Dockerspawner and JupyterHub

- [Reporting Issues](https://github.com/jupyterhub/dockerspawner/issues)
- JupyterHub tutorial | [Repo](https://github.com/jupyterhub/jupyterhub-tutorial)
  | [Tutorial documentation](http://jupyterhub-tutorial.readthedocs.io/en/latest/)
- [Documentation for JupyterHub](http://jupyterhub.readthedocs.io/en/latest/) | [PDF (latest)](https://media.readthedocs.org/pdf/jupyterhub/latest/jupyterhub.pdf) | [PDF (stable)](https://media.readthedocs.org/pdf/jupyterhub/stable/jupyterhub.pdf)
- [Documentation for JupyterHub's REST API](http://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/jupyterhub/master/docs/rest-api.yml#/default)

### Project Jupyter

- [Documentation for Project Jupyter](http://jupyter.readthedocs.io/en/latest/index.html) | [PDF](https://media.readthedocs.org/pdf/jupyter/latest/jupyter.pdf)
- [Project Jupyter website](https://jupyter.org)