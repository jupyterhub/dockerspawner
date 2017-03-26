# Build as jupyterhub/systemuser
# Run with the DockerSpawner in JupyterHub

FROM jupyterhub/singleuser

MAINTAINER Project Jupyter <jupyter@googlegroups.com>

USER root

WORKDIR /home
RUN userdel jovyan && rm -rf /home/jovyan
ENV SHELL /bin/bash

#while waiting for PR in jupyter/docker-stacks, keep the same naming conventions
ADD systemuser.sh /usr/local/bin/start-systemuser.sh

# smoke test entrypoint
RUN USER_ID=65000 USER=systemusertest sh /usr/local/bin/start-systemuser.sh -h && userdel systemusertest

CMD ["sh", "/usr/local/bin/start-systemuser.sh"]
