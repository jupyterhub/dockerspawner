# internal SSL configuration with Docker

JupyterHub 1.0 introduces internal_ssl configuration for encryption and authentication of all internal communication.

DockerSpawner implements the `.move_certs` method necessary,
so no additional configuration

This directory contains a docker-compose configuration to deploy jupyterhub 1.0
with configurable-http-proxy and total internal encryption.

To use it:

    docker network create jupyterhub
    docker volume create jupyterhub-ssl  jupyterhub-data

    docker-compose build
    docker-compose up

and then visit http://127.0.0.1:8000

The setup uses dummy authenticator, so you can login with any username and password.
