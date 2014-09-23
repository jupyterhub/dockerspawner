# Configuration file for Jupyter Hub

c = get_config()

c.JupyterHubApp.authenticator_class = 'oauthenticator.GitHubOAuthenticator'

c.Authenticator.whitelist = whitelist = set()
c.JupyterHubApp.admin_users = admin = set()

import os

join = os.path.join
here = os.path.dirname(__file__)
with open(join(here, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        whitelist.add(name)
        if len(parts) > 1 and parts[1] == 'admin':
            admin.add(name)

c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# ssl config
ssl = join(here, 'ssl')
keyfile = join(ssl, 'ssl.key')
certfile = join(ssl, 'ssl.cert')
if os.path.exists(keyfile):
    c.JupyterHubApp.ssl_key = keyfile
if os.path.exists(certfile):
    c.JupyterHubApp.ssl_cert = certfile
