# Build as jupyter/jupyterhub-systemuser
# Run with the DockerSpawner in JupyterHub

FROM ipython/scipystack

MAINTAINER IPython Project <ipython-dev@scipy.org>

# fetch juptyerhub-systemuser entrypoint
ADD https://raw.githubusercontent.com/jupyter/jupyterhub/master/jupyterhub/systemuser.py /usr/local/bin/jupyterhub-systemuser
RUN chmod 755 /usr/local/bin/jupyterhub-systemuser

# set the shell
ENV SHELL /bin/bash

EXPOSE 8888

# When the image is built, we want to add the user to the system. So, this looks
# for a file called `user` which contains one line of the format username:userid
# (e.g. jupyter:1005)
ADD adduser.sh /srv/singleuser/adduser.sh
ONBUILD ADD user /srv/singleuser/user
ONBUILD RUN ["sh", "/srv/singleuser/adduser.sh"]

ADD singleuser.sh /srv/singleuser/singleuser.sh
CMD ["sh", "/srv/singleuser/singleuser.sh"]
