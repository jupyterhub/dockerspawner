# Designed to be run as 
# 
# docker run -it -p 9999:8888 jupyter/jhubnghub

FROM ipython/scipystack

MAINTAINER IPython Project <ipython-dev@scipy.org>

# install js dependencies
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y npm nodejs-legacy
RUN npm install -g bower less
RUN npm install -g jupyter/configurable-http-proxy

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

RUN mkdir /srv/oauthenticator
WORKDIR /srv/oauthenticator
ENV PYTHONPATH /srv/oauthenticator

ADD jupyter_hub_config.py /srv/oauthenticator/jupyter_hub_config.py
ADD oauthenticator.py /srv/oauthenticator/oauthenticator.py
ADD onbuild.sh /srv/oauthenticator/onbuild.sh

EXPOSE 8000

# Should these be ONBUILD?
ADD userlist /srv/oauthenticator/userlist
RUN ["sh", "/srv/oauthenticator/onbuild.sh"]

ADD run.sh /srv/oauthenticator/run.sh
CMD ["sh", "/srv/oauthenticator/run.sh"]
