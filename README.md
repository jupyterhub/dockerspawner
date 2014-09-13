gitorn
======

Tornado + GitHub OAuth Toy

Simple Demo of setting up GitHub OAuth with Tornado

### Installation

```
pip install tornado
```

### Development

You'll need a client ID and client secret from GitHub, which you can get from:

https://github.com/settings/applications/new

or, if using an organization:

https://github.com/organizations/<your_org>/settings/applications/

Then fire up `toy.py` with environment variables for client id and client secret set.

```
GITHUB_CLIENT_ID=<client_id> GITHUB_CLIENT_SECRET=<client_secret>  python toy.py
```
