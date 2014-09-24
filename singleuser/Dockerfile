# Build as jupyter/jupyterhub-singleuser
# Run with the DockerSpawner in JupyterHub

FROM ipython/scipystack

MAINTAINER IPython Project <ipython-dev@scipy.org>

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y npm nodejs-legacy
RUN npm install -g bower less

# Can't directly add the source as it won't have the submodules
RUN mkdir -p /srv/
WORKDIR /srv/
RUN git clone --recursive --depth 1 https://github.com/ipython/ipython.git

WORKDIR /srv/ipython/
RUN chmod a+rw /srv/ipython/examples

# Installing build dependencies directly
RUN pip2 install fabric
RUN pip3 install fabric

RUN python setup.py submodule

# .[all] only works with -e
# Can't use -e because ipython2 and ipython3 will clobber each other
RUN pip2 install .
RUN python2 -m IPython kernelspec install-self --system
RUN pip3 install .
RUN python3 -m IPython kernelspec install-self --system

# install jupyterhub
WORKDIR /srv/
RUN git clone --recursive --depth 1 https://github.com/jupyter/jupyterhub.git
WORKDIR /srv/jupyterhub/

RUN pip3 install -r requirements.txt
RUN pip3 install .

RUN mkdir /srv/singleuser

# jupyter is our user
RUN useradd -m -s /bin/bash jupyter

USER jupyter
ENV HOME /home/jupyter
ENV SHELL /bin/bash
ENV USER jupyter

WORKDIR /home/jupyter/

# IPython introductions
RUN cp -r /srv/ipython/examples /home/jupyter/examples

EXPOSE 8888

ADD singleuser.sh /srv/singleuser/singleuser.sh
CMD ["sh", "/srv/singleuser/singleuser.sh"]
