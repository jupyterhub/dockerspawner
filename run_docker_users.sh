here=$(dirname $0)
export PYTHONPATH=$here

# load github auth from env
source $here/env
export GITHUB_CLIENT_ID
export GITHUB_CLIENT_SECRET
export OAUTH_CALLBACK_URL

jupyterhub -f jupyter_hub_config_docker.py $@

