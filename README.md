# DockerSpawner

This is an example of using a custom Spawner and Authenticator with JuptyerHub.

GitHub OAuth + JuptyerHub = [OAuthenticator](https://github.com/jupyter/oauthenticator).

Add docker, and you have something pretty nifty.

This is an example of running [JupyterHub](https://github.com/jupyter/jupyterhub)
with [GitHub OAuth](https://developer.github.com/v3/oauth/) for authentication,
spinning up a [docker](https://www.docker.com/) container for each user.

## setup

Install dependencies:

    pip install -r requirements.txt

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

## build

Build the container with:

    docker build -t jupyter/singleuser singleuser

### ssl

To run the server on HTTPS, put your ssl key and cert in ssl/ssl.key and ssl/ssl.cert.

## run

Add your oauth client id, client secret, and callback URL to the `env file`.
Once you have built the container, you can run the server with:

    sh run.sh

Which will run the JupyterHub server. When users login, a container will be created for them.
