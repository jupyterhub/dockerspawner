# Using SwarmSpawner

## Create a swarm cluster

If you already have a swarm cluster, skip this section.

To make this a complete example,
let's create a local swarm cluster with virtualbox.
We will have one manager and two workers.

```bash
docker-machine create --driver virtualbox swarm-manager
docker-machine create --driver virtualbox swarm1
docker-machine create --driver virtualbox swarm2
```

Make `swarm-manager` the manager

```bash
MANAGER_IP=$(docker-machine ip swarm-manager)
docker-machine ssh swarm-manager "docker swarm init --advertise-addr $MANAGER_IP"
docker_join_command=$(docker-machine ssh swarm-manager "docker swarm join-token worker" | grep "^\s*docker")
```

which will have output like:

```
To add a worker to this swarm, run the following command:

    docker swarm join --token ...
```

Run the join command we captured on on your workers:

```bash
docker-machine ssh swarm1 "$docker_join_command"
docker-machine ssh swarm2 "$docker_join_command"
```

You should see the output:

```
This node joined a swarm as a worker.
```

Now we can connect to the cluster and verify that it exists:

```bash
eval $(docker-machine env swarm-manager)
docker node ls
```

```
ID                            HOSTNAME        STATUS    AVAILABILITY   MANAGER STATUS   ENGINE VERSION
mggnoy17xh8z78lz4pm8npn2x     swarm1          Ready     Active                          19.03.12
jwlechv3wf7zc7ynm8lshewii     swarm2          Ready     Active                          19.03.12
pjw8sebqsc3ervzlvhdayfbpl *   swarm-manager   Ready     Active         Leader           19.03.12
```

## Using SwarmSpawner

In general, when configuring a Spawner, there is one primary concern to get it working: **Make sure the servers can connect to the Hub**.
This generally takes the form of network configuration of the Hub,
and possibly also the Spawner.

This directory contains an example `docker-compose.yml` that does the following:

#. configures jupyterhub to use `dummyauthenticator` (for testing) and `SwarmSpawner`
#. runs the hub and proxy in separate containers
#. creates an `overlay` network `swarm_jupyterhub-net` so that everybody can communicate across the swarm

The key parts of jupyterhub configuration make the Hub accessible on the docker network. First, make sure that the Hub is connectable from outside its own container:

```python
c.JupyterHub.hub_ip = '0.0.0.0'
```

Then, tell everyone (singleuser servers and proxy)
to connect to it using it's hostname on the docker network
(this is the name of the service running the jupyterhub image):

```python
c.JupyterHub.hub_connect_ip = 'hub'
```

Finally, we need to put user servers onto the same network as the Hub.
In `docker-compose.yml`, we created a network called `jupyterhub-net`,
and put the hub and proxy on it:

```yaml
networks:
  jupyterhub-net:
    driver: overlay
```

However, docker-compose _actually_ created this network as `swarm_jupyterhub-net`,
and that's the name we need to pass to the Spawner:

```python
c.SwarmSpawner.network_name = 'swarm_jupyterhub-net'
```

## Running the example

Build the jupyterhub image:

```bash
docker-compose build
```

Finally, start jupyterhub:

```bash
docker-compose up
```

At this point, you should be able to go to `http://$(docker-machine ip swarm-manager)` and test spawning.
