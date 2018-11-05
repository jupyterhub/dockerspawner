# Using SwarmSpawner

## Create a swarm cluster

If you already have a swarm cluster, skip this section.

To make this a complete example,
let's create a local swarm cluster with virtualbox.
We will have one master and two workers.

```bash
docker-machine create --driver virtualbox swarm-master
docker-machine create --driver virtualbox swarm1
docker-machine create --driver virtualbox swarm2
```

Make `swarm-master` the master

```bash
MASTER_IP=$(docker-machine ip swarm-master)
docker-machine ssh swarm-master "docker swarm init --advertise-addr $MASTER_IP"
docker_join_command=$(docker-machine ssh swarm-master "docker swarm join-token worker" | grep "^\s*docker")
```

which will have output like:

```
To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-67asaufw4gdn7tclwwvs09xyytc12alwgf1qdozlcjyp4og5ps-cqpokgek9ml3gahxv7cvz0rm9 192.168.99.101:2377
```

Copy that `docker swarm join` command and run it on on your workers:

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
eval $(docker-machine env swarm-master)
docker node ls
```

```
ID                            HOSTNAME            STATUS              AVAILABILITY        MANAGER STATUS      ENGINE VERSION
vnvw9ym4n7fxsqmzx1ut9z23h     swarm1              Ready               Active                                  18.06.1-ce
m3a1as22uoavuf5jayy24hx87     swarm2              Ready               Active                                  18.06.1-ce
vz8n6gw6m0ve1a7gk0micxa4n *   swarm-master        Ready               Active              Leader              18.06.1-ce
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

However, docker-compose *actually* created this network as `swarm_jupyterhub-net`,
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

```
docker-compose up
```


At this point, you should be able to go to `http://$(docker-machine ip swarm-master)` and test spawning.
