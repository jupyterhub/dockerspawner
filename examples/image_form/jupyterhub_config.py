c = get_config()  # noqa


options_form_tpl = """
<label for="image">Image</label>
<input name="image" class="form-control" placeholder="the image to launch (default: {default_image})"></input>
"""


def get_options_form(spawner):
    return options_form_tpl.format(default_image=spawner.image)


c.DockerSpawner.options_form = get_options_form

# specify that DockerSpawner should accept any image from user input
c.DockerSpawner.allowed_images = "*"

# tell JupyterHub to use DockerSpawner
c.JupyterHub.spawner_class = "docker"

# the rest of the config is testing boilerplate
# to make the Hub connectable from the containers

# dummy for testing. Don't use this in production!
c.JupyterHub.authenticator_class = "dummy"
# while using dummy auth, make the *public* (proxy) interface private
c.JupyterHub.ip = "127.0.0.1"

# we need the hub to listen on all ips when it is in a container
c.JupyterHub.hub_ip = "0.0.0.0"

# may need to set hub_connect_ip to be connectable to containers
# default hostname behavior usually works, though
# c.JupyterHub.hub_connect_ip

# pick a default image to use when none is specified
c.DockerSpawner.image = "jupyter/base-notebook"

# delete containers when they stop
c.DockerSpawner.remove = True
