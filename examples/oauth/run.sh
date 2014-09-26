here="$(dirname $0)"
export PYTHONPATH="$here:$here/../..:$PYTHONPATH"

test -f oauthenticator.py || curl https://raw.githubusercontent.com/jupyter/oauthenticator/master/oauthenticator.py > oauthenticator.py
# load github auth from env
source $here/env

jupyterhub $@

