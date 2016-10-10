# jupyterhub/singleuser

Built from the `jupyter/scipy-notebook` base image.

This image contains a single user notebook server for use with
[JupyterHub](https://github.com/jupyterhub/jupyterhub). In particular, it is meant
to be used with the
[DockerSpawner](https://github.com/jupyterhub/dockerspawner/blob/master/dockerspawner/dockerspawner.py)
class to launch user notebook servers within docker containers.

This particular server runs (within the container) as the `jupyter` user, with
home directory at `/home/jupyter`, and the IPython example notebooks at
`/home/jupyter/examples`.

## Important note on persistence

This home directory, `/home/jupyter`, is *not* persistent; thus,
this image should be used with temporary or demonstration JupyterHub
servers.

If you would like persistence of data, additional configuration is
required. See [jupyterhub/jupyterhub-deploy-docker][jupyterhub-deploy-docker]'s
documentation on [Creating a JupyterHub data volume][data volume] and
[How can I backup a user's notebook directory][backup user directory]
for configuration information about persistence and mounting a docker volume.
You may also find the [official Docker documentation on data volumes][docker data volumes] helpful.


  [jupyterhub-deploy-docker]: (https://github.com/jupyterhub/jupyterhub-deploy-docker)
  [data volume]: https://github.com/jupyterhub/jupyterhub-deploy-docker#create-a-jupyterhub-data-volume
  [backup user directory]: https://github.com/jupyterhub/jupyterhub-deploy-docker#how-can-i-backup-a-users-notebook-directory
  [Docker data volumes]: https://docs.docker.com/engine/tutorials/dockervolumes/
