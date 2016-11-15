**[Prerequisites](#prerequisites)** |
**[Installation](#installation)** |
**[Configuration](#configuration)** |
**[Building the Docker images](#building-the-docker-images)** |
**[Contributing](#contributing)** |
**[License](#license)** |
**[Getting help](#getting-help)**


# DockerSpawner

**DockerSpawner** enables [JupyterHub](https://github.com/jupyterhub/jupyterhub) 
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

Two basic types of spawners are available for dockerspawner:

- [DockerSpawner](#DockerSpawner): useful if you would like to spawn 
  single user notebook servers on the fly. It will take an
  authenticated user and spawn a notebook server in a Docker container
  for the user.

- [SystemUserSpawner](#SystemUserSpawner): useful if you would like to
  spawn single user notebook servers that correspond to the system's 
  users.

In most cases, we recommend using DockerSpawner. Use cases where you
may wish to use SystemUserSpawner are:

- You are using docker just for environment management, but are running
  on a system where the users already have accounts and files they
  should be able to access from within the container. For example, you
  wish to use the system users and user home directories that
  already exist on a system.
- You are using an external service, such as nbgrader, that relies on 
  distinct unix user ownership and permissions.
  
If neither of those cases applies, DockerSpawner is probably the right
choice.


### DockerSpawner

Tell JupyterHub to use DockerSpawner by adding the following line to 
your `jupyterhub_config.py`:

```python
    c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
```

There is a complete example in [examples/oauth](examples/oauth) for
using GitHub OAuth to authenticate users, and spawn containers with docker.

### SystemUserSpawner

If you want to spawn notebook servers for users that correspond to system users,
you can use the SystemUserSpawner instead. Add the following to your
`jupyterhub_config.py`:

```python
    c.JupyterHub.spawner_class = 'dockerspawner.SystemUserSpawner'
```

The SystemUserSpawner will also need to know where the user home directories
are on the host. By default, it expects them to be in `/home/<username>`, but if
you want to change this, you'll need to further modify the
`jupyterhub_config.py`. For example, the following will look for a user's home
directory on the host system at `/volumes/user/<username>`:

```python
    c.SystemUserSpawner.host_homedir_format_string = '/volumes/user/{username}'
```

For a full example of how `SystemUserSpawner` is used, see the
[compmodels-jupyterhub](https://github.com/jhamrick/compmodels-jupyterhub)
repository (this additionally runs the JupyterHub server within a docker
container, and authenticates users using GitHub OAuth).

### Using Docker Swarm

Both `DockerSpawner` and `SystemUserSpawner` are compatible with
[Docker Swarm](https://docs.docker.com/swarm/) when multiple system
nodes will be used in a cluster for JupyterHub. Simply add `0.0.0.0`
to your `jupyterhub_config.py` file as the `container_ip`:

```python
c.DockerSpawner.container_ip = "0.0.0.0"
```

This will configure DockerSpawner and SystemUserSpawner to get
the container IP address and port number using the `docker port`
command.

### Data persistence and DockerSpawner

With `DockerSpawner`, the user's home directory
is *not* persistent by default, so some configuration is required to do so unless
the directory is to be used with temporary or demonstration JupyterHub
deployments.

The simplest version of persistence to the host filesystem is to
isolate users in the filesystem, but leave everything owned by the same
'actual' user with DockerSpawner. That is, using docker mounts to
isolate user files, not ownership or permissions on the host.

Volume mapping for DockerSpawner in `jupyterhub_config.py`
is required configuration for persistence. To map volumes from 
the host file/directory to the container (referred to as guest)
file/directory mount point, set the `c.DockerSpawner.volumes` to specify
the guest mount point (bind) for the volume.

If you use `{username}` in either the host or guest file/directory path,
username substitution will be done and `{username}` will be replaced with
the current user's name.

(Note: The jupyter/docker-stacks notebook images run the Notebook server as user
`jovyan` and set the user's notebook directory to `/home/jovyan/work`.)


```python
# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
```

The [`jupyterhub-deploy-docker`](https://github.com/jupyterhub/jupyterhub-deploy-docker) repo
contains a reference deployment that persists the notebook directory; 
see its [`jupyterhub_config.py`](https://github.com/jupyterhub/jupyterhub-deploy-docker/blob/master/jupyterhub_config.py)
for an example configuration.

See Docker documentation on [data volumes] for more information on data
persistence. 

## Memory limits

If you have `jupyterhub >= 0.7`, you can set a memory limit for each user's container easily.

```
c.Spawner.mem_limit = '2G'
```

The value can either be an integer (bytes) or a string with a 'K', 'M', 'G' or 'T' prefix.

## Building the Docker images

### Single user notebook server

Build the `jupyterhub/singleuser` container with:

```bash
    docker build -t jupyterhub/singleuser singleuser
```

You may also use `docker pull jupyterhub/singleuser` to download the
container from [Docker Hub](https://registry.hub.docker.com/u/jupyterhub/singleuser/).

### System user notebook server

This is used with [`SystemUserSpawner`](#systemuserspawner).

Build the `jupyterhub/systemuser` container with:

```bash
    docker build -t jupyterhub/systemuser systemuser
```

You may also use `docker pull jupyterhub/systemuser` to download the
containter from [Docker Hub](https://registry.hub.docker.com/u/jupyterhub/systemuser/).


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


  [data volumes]: https://docs.docker.com/engine/tutorials/dockervolumes/#/data-volumes

  