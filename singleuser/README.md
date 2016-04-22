# jupyterhub/singleuser

Built from the `jupyter/scipy-notebook` base image.

This image contains a single user notebook server for use with
[JupyterHub](https://github.com/jupyterhub/jupyterhub). In particular, it is meant
to be used with the
[DockerSpawner](https://github.com/jupyterhub/dockerspawner/blob/master/dockerspawner/dockerspawner.py)
class to launch user notebook servers within docker containers.

This particular server runs (within the container) as the `jupyter` user, with
home directory at `/home/jupyter`, and the IPython example notebooks at
`/home/jupyter/examples`. This home directory is *not* persistent by default;
thus, this image should be used with temporary or demonstration JupyterHub
servers.
