# jupyter/systemuser

This image contains a single user notebook server for use with
[JupyterHub](https://github.com/jupyter/jupyterhub). In particular, it is meant
to be used with the
[SystemUserSpawner](https://github.com/jupyter/dockerspawner/blob/master/dockerspawner/systemuserspawner.py)
class to launch user notebook servers within docker containers.

This particular server initially runs (within the container) as the `root` user.
When the container is run, it expects to have access to environment variables
for `$USER` and `$USER_ID`. It will create a user inside the container with the
specified username and id, and then run the notebook server as that user (using
`sudo`). Similarly, it expects the user's home directory to be mounted as a
volume in the container when it is run.
