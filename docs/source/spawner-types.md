## Choosing a spawner

Three basic types of spawners are available for dockerspawner:

- [DockerSpawner][ln-spawner-docker]: useful if you would like to spawn 
  single user notebook servers on the fly. It will take an
  authenticated user and spawn a notebook server in a Docker container
  for the user.

- [SwarmSpawner][ln-spawner-swarm]: same behavior as DockerSpawner, but
  launches single user notebook servers as Docker Swarm mode services
  instead of as individual containers. This allows for running JupyerHub
  in a swarm so that notebook containers can be run on any of multiple
  servers.

- [SystemUserSpawner][ln-spawner-sysusr]: useful if you would like to
  spawn single user notebook servers that correspond to the system's 
  users.

[ln-spawner-docker]: #dockerspawner
[ln-spawner-swarm]: #swarmspawner
[ln-spawner-sysusr]: #systemuserspawner

  
In most cases, we recommend using DockerSpawner. Use cases where you
may wish to use SystemUserSpawner are:

- You are using docker just for environment management, but are running
  on a system where the users already have accounts and files they
  should be able to access from within the container. For example, you
  wish to use the system users and user home directories that
  already exist on a system.
- You are using an external service, such as nbgrader, that relies on 
  distinct unix user ownership and permissions.
  
---
**Note:**
If neither of those cases applies, DockerSpawner is probably the right
choice.

---

### DockerSpawner

Tell JupyterHub to use DockerSpawner by adding the following line to 
your `jupyterhub_config.py`:

```python
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
```

There is a complete example in [examples/oauth](https://github.com/jupyterhub/dockerspawner/tree/master/examples/oauth)
for using GitHub OAuth to authenticate users, and spawn containers with docker.

### SwarmSpawner

Tell JupyterHub to use SwarmSpawner by adding the following line to
your `jupyterhub_config.py`:

```python
c.JupyterHub.spawner_class = 'dockerspawner.SwarmSpawner'
```

You need to make sure that the JupyterHub process is launched on a Swarm manager
node, since its node needs to have permission to launch new Swarm services. It also
needs to have the docker socket mounted (like DockerSpawner) to communicate out of its
own container with the host's docker server. You can accomplish this in your
`docker-compose.yml` with the following settings:

```yaml
jupyterhub:
  image: jupyterhub/jupyterhub
  # This is necessary to prevent the singleton hub from using its service number as its hostname
  hostname: jupyterhub
  # Permit communication with the host's docker server
  volumes:
    - "/var/run/docker.sock:/var/run/docker.sock"
  # Ensure Hub and Notebook servers are on the same network
  networks:
    - jupyterhub_network
  environment:
    DOCKER_NETWORK_NAME: jupyterhub_network
  # Ensure that we execute on a Swarm manager
  deploy:
    replicas: 1
    placement:
      constraints:
        - node.role == manager
```

You'll also need to ensure that the JupyterHub service and the launched single-user
services all run on the same Swarm overlay network. You can create one easily using:

```bash
$ docker network create --driver overlay jupyterhub_network
```

Then use this network in your jupyterhub_config.py like the following example:

```python
network_name = os.environ['DOCKER_NETWORK_NAME']
c.SwarmSpawner.network_name = network_name
c.SwarmSpawner.extra_host_config = {'network_mode': network_name}
```

Unless otherwise noted, SwarmSpawner supports the same configuration options as DockerSpawner.

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

### Using Docker Swarm (not swarm mode!)

**Note:** This is the older Docker Swarm, which makes a swarm look like a single docker instance.
For the newer Docker Swarm Mode, see [SwarmSpawner][ln-spawner-swarm]. This used to be supported by
[cassinyio](https://github.com/cassinyio/SwarmSpawner), but this repository has been deprecated.

Both `DockerSpawner` and `SystemUserSpawner` are compatible with
[Docker Swarm](https://docs.docker.com/swarm/) when multiple system
nodes will be used in a cluster for JupyterHub. Simply add `0.0.0.0`
to your `jupyterhub_config.py` file as the `host_ip`:

```python
c.DockerSpawner.host_ip = "0.0.0.0"
```

This will configure DockerSpawner and SystemUserSpawner to get
the container IP address and port number using the `docker port`
command.
