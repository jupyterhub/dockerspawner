# DockerSpawner

Enables [JupyterHub](https://github.com/jupyterhub/jupyterhub) to spawn
user servers in docker containers.

This is an example of running [JupyterHub](https://github.com/jupyterhub/jupyterhub)
with [GitHub OAuth](https://github.com/jupyterhub/oauthenticator) for authentication,
spinning up a [docker](https://www.docker.com/) container for each user.

## setup

(I assume you have installed dockerspawner dependencies and built the single-user container already)

Install oauthenticator:

    pip install oauthenticator


Make a file called `userlist` with one GitHub user name per line.
If that user should be an admin (you!), add `admin` after a space.

For example:

```
echo admin
alpha
sierra
victor
```


Create a [GitHub oauth application](https://github.com/settings/applications/new).
Make sure the callback URL is:

    http[s]://[your-host]/hub/oauth_callback

Where `[your-host]` is where your server will be running. Such as `example.com:8000`.
Add your oauth client id, client secret, and callback URL to the `env file`.
Note: The client secret should not be visible publicly. Use caution if
placing `env file` in version control.


### ssl

To run the server on HTTPS, put your ssl key and cert in ssl/ssl.key and ssl/ssl.cert.

## run

You can run the server with:

    bash run.sh

Which will run the JupyterHub server, loading your GitHub credentials from `env`.
When users login, a container will be created for them. Like magic!
