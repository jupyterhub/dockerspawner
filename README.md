# OAuthenticator

GitHub OAuth + JuptyerHub Authenticator = OAuthenticator

Example of running [JupyterHub]() with [GitHub OAuth]() for authentication.

## setup

Make a file called `userlist` with one GitHub user name per line.
If that user should be an admin (you!), add `admin` after a space.

For example:

```
mal admin
zoe admin
wash
inara admin
kaylee
jayne
simon
river
```


Create a [GitHub oauth application](https://github.com/settings/applications/new).
Make sure the callback URL is:

    http[s]://[your-host]/hub/oauth_callback

Where `[your-host]` is where your server will be running. Such as `example.com:8000`.

## build

Build the container with:

    docker build -t jupyter/oauthenticator .

## run

Once you have built the container, you can run it with:

    docker run -it -p 9000:8000 -E GITHUB_CLIENT_ID=$GITHUB_CLIENT_ID \
      -E GITHUB_CLIENT_SECRET=$GITHUB_CLIENT_SECRET \
      -E OAUTH_CALLBACK_URL=$OAUTH_CALLBACK_URL \
      jupyter/oauthenticator

Which will run the Jupyter server.

If you want to avoid all the `-E` arguments,
you can add the relevant exports to `run.sh` before you build the container.

