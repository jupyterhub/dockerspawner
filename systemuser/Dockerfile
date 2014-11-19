# Build as jupyter/systemuser
# Run with the DockerSpawner in JupyterHub

FROM ipython/scipystack

MAINTAINER IPython Project <ipython-dev@scipy.org>

# fetch juptyerhub-singleuser entrypoint
ADD https://raw.githubusercontent.com/jupyter/jupyterhub/master/jupyterhub/singleuser.py /usr/local/bin/jupyterhub-singleuser
RUN chmod 755 /usr/local/bin/jupyterhub-singleuser

EXPOSE 8888

ENV SHELL /bin/bash

ADD systemuser.sh /srv/singleuser/systemuser.sh
CMD ["sh", "/srv/singleuser/systemuser.sh"]
