# jupyterhub/systemuser

Built from the `jupyter/scipy-notebook` base image.

This image contains a single user notebook server for use with
[JupyterHub](https://github.com/jupyterhub/jupyterhub). In particular, it is meant
to be used with the
[SystemUserSpawner](https://github.com/jupyterhub/dockerspawner/blob/master/dockerspawner/systemuserspawner.py)
class to launch user notebook servers within docker containers.

This particular server initially runs (within the container) as the `root` user.
When the container is run, it expects to have access to environment variables
for `$USER`, `$USER_ID`, and `$HOME`. It will create a user inside the container
with the specified username and id, and then run the notebook server as that
user (using `sudo`). It also expects the user's home directory (specified by
`$HOME`) to exist -- for example, by being mounted as a volume in the container
when it is run.
