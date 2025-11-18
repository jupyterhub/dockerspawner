# Data persistence

With `DockerSpawner`, the user's home directory is **not** persistent by default,
so some configuration is required to do so unless the directory is to be used
with temporary or demonstration JupyterHub deployments.

The simplest version of persistence to the host filesystem is to
isolate users in the filesystem, but leave everything owned by the same
'actual' user with DockerSpawner. That is, using **docker mounts** to
isolate user files, not ownership or permissions on the host.

## Volume mapping

Volume mapping for DockerSpawner in `jupyterhub_config.py`
is required configuration for persistence. To map volumes from
the host file/directory to the container (referred to as guest)
file/directory mount point, set the `c.DockerSpawner.volumes` to specify
the guest mount point (bind) for the volume.

If you use `{username}` in either the host or guest file/directory path,
username substitution will be done and `{username}` will be replaced with
the current user's name.

```{note}
The jupyter/docker-stacks notebook images run the Notebook server as user
`jovyan` and set the user's notebook directory to `/home/jovyan/work`.
```

Example:

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

# Mount a directory on the host to the notebook user's notebook directory in the container
c.DockerSpawner.mounts = [
  {'source': '/jupyterhub-user-{username}', 'target': notebook_dir, 'type': 'bind'}
]
```

## Memory limits

If you have `jupyterhub >= 0.7`, you can set a memory limit for each user's container easily.

```
c.Spawner.mem_limit = '2G'
```

The value can either be an integer (bytes) or a string with a 'K', 'M', 'G' or 'T' suffix.

## Resources

The [`jupyterhub-deploy-docker`](https://github.com/jupyterhub/jupyterhub-deploy-docker) repo
contains a reference deployment that persists the notebook directory;
see its [`jupyterhub_config.py`](https://github.com/jupyterhub/jupyterhub-deploy-docker/blob/master/jupyterhub_config.py)
for an example configuration.

See Docker documentation on [data volumes](https://docs.docker.com/storage/volumes/) for more information on data
persistence.
