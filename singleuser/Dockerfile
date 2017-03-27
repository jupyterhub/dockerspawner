# Build as jupyterhub/singleuser
# Run with the DockerSpawner in JupyterHub

FROM jupyter/scipy-notebook

MAINTAINER Project Jupyter <jupyter@googlegroups.com>

# no need for singleuser Dockerfile anymore,
# all scripts have been ported to jupyter/base-notebook docker image

# smoke test that it's importable at least
RUN sh /usr/local/bin/start-singleuser.sh -h
CMD ["sh", "/usr/local/bin/start-singleuser.sh"]
