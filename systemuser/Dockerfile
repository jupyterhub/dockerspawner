# Build as jupyter/systemuser
# Run with the DockerSpawner in JupyterHub

FROM ipython/scipystack

MAINTAINER IPython Project <ipython-dev@scipy.org>

# fetch juptyerhub-singleuser entrypoint
ADD https://raw.githubusercontent.com/jupyter/jupyterhub/master/jupyterhub/singleuser.py /usr/local/bin/jupyterhub-singleuser
RUN chmod 755 /usr/local/bin/jupyterhub-singleuser

# jupyter is our (initial) user
RUN useradd -s /bin/bash jupyter

USER jupyter
ENV SHELL /bin/bash

EXPOSE 8888

ADD systemuser.sh /srv/singleuser/systemuser.sh
CMD ["sh", "/srv/singleuser/systemuser.sh"]
