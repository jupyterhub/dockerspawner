import pwd

from dockerspawner import DockerSpawner
from textwrap import dedent
from traitlets import (
    Integer,
    Unicode,
)
from tornado import gen


class SystemUserSpawner(DockerSpawner):

    container_image = Unicode("jupyterhub/systemuser", config=True)

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

    image_homedir_format_string = Unicode(
        "/home/{username}",
        config=True,
        help=dedent(
            """
            Format string for the path to the user's home directory
            inside the image.  The format string should include a
            `username` variable, which will be formatted with the
            user's username.
            """
        )
    )

    user_id = Integer(-1,
        help=dedent(
            """
            If system users are being used, then we need to know their user id
            in order to mount the home directory.

            User IDs are looked up in two ways:

            1. stored in the state dict (authenticator can write here)
            2. lookup via pwd
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
        return self.image_homedir_format_string.format(username=self.user.name)

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

    def get_env(self):
        env = super(SystemUserSpawner, self).get_env()
        env.update(dict(
            USER=self.user.name,
            USER_ID=self.user_id,
            HOME=self.homedir
        ))
        return env
    
    def _user_id_default(self):
        """
        Get user_id from pwd lookup by name
        
        If the authenticator stores user_id in the user state dict,
        this will never be called, which is necessary if
        the system users are not on the Hub system (i.e. Hub itself is in a container).
        """
        return pwd.getpwnam(self.user.name).pw_uid

    def load_state(self, state):
        super().load_state(state)
        if 'user_id' in state:
            self.user_id = state['user_id']

    def get_state(self):
        state = super().get_state()
        if self.user_id >= 0:
            state['user_id'] = self.user_id
        return state

    @gen.coroutine
    def start(self, image=None):
        """start the single-user server in a docker container"""
        yield super(SystemUserSpawner, self).start(
            image=image,
            extra_create_kwargs={'working_dir': self.homedir}
        )
