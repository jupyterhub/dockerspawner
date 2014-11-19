from dockerspawner import DockerSpawner
from textwrap import dedent
from IPython.utils.traitlets import (
    Dict,
    Unicode,
)
from tornado import gen


class SystemUserSpawner(DockerSpawner):

    host_homedir_format_string = Unicode(
        "/home/{username}",
        config=True,
        help=dedent(
            """
            Format string for the path to the user's home directory on the host.
            The format string should include a `username` variable, which will
            be formatted with the user's username.
            """
        )
    )

    user_ids = Dict(
        config=True,
        help=dedent(
            """
            If system users are being used, then we need to know their user id
            in order to mount the home directory. User ids should be specified
            in this dictionary.
            """
        )
    )

    @property
    def host_homedir(self):
        """
        Path to the volume containing the user's home directory on the host.
        """
        return self.host_homedir_format_string.format(username=self.user.name)

    @property
    def homedir(self):
        """
        Path to the user's home directory in the docker image.
        """
        return "/home/{username}".format(username=self.user.name)

    @property
    def volume_mount_points(self):
        """
        Volumes are declared in docker-py in two stages.  First, you declare
        all the locations where you're going to mount volumes when you call
        create_container.

        Returns a list of all the values in self.volumes or
        self.read_only_volumes.
        """
        mount_points = super(SystemUserSpawner, self).volume_mount_points
        mount_points.append(self.homedir)
        return mount_points

    @property
    def volume_binds(self):
        """
        The second half of declaring a volume with docker-py happens when you
        actually call start().  The required format is a dict of dicts that
        looks like:

        {
            host_location: {'bind': container_location, 'ro': True}
        }
        """
        volumes = super(SystemUserSpawner, self).volume_binds
        volumes[self.host_homedir] = {
            'bind': self.homedir,
            'ro': False
        }
        return volumes

    def _env_default(self):
        env = super(SystemUserSpawner, self)._env_default()
        env.update(dict(
            USER=self.user.name,
            USER_ID=self.user_ids[self.user.name],
            HOME=self.homedir
        ))
        return env

    @gen.coroutine
    def start(self, image=None):
        """start the single-user server in a docker container"""
        yield super(SystemUserSpawner, self).start(
            image=image,
            working_dir=self.homedir
        )
