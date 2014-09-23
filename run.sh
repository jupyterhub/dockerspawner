#!/bin/bash
# To set oauth at build time,
# uncomment these with your appropriate values.
# Otherwise, run with `docker run -E GITHUB_CLIENT_ID=asdf,...`
#
# export GITHUB_CLIENT_ID=
# export GITHUB_CLIENT_SECRET=
# export OAUTH_CALLBACK_URL=

jupyterhub --debug
