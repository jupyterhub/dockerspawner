here=$(dirname $0)
export PYTHONPATH=$here

test -f oauthenticator.py || curl https://raw.githubusercontent.com/jupyter/oauthenticator/master/oauthenticator.py > oauthenticator.py
# load github auth from env
source $here/env
export GITHUB_CLIENT_ID
export GITHUB_CLIENT_SECRET
export OAUTH_CALLBACK_URL

jupyterhub $@

