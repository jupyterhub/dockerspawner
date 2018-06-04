from dockerspawner import DockerSpawner
from textwrap import dedent
from traitlets import (
    Integer,
    Unicode,
)


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
        # relies on NB_USER and NB_UID handling in jupyter/docker-stacks
        env.update(dict(
            USER=self.user.name, # deprecated
            NB_USER=self.user.name,
            USER_ID=self.user_id, # deprecated
            NB_UID=self.user_id,
            HOME=self.homedir,
        ))
        return env

    def _user_id_default(self):
        """
        Get user_id from pwd lookup by name

        If the authenticator stores user_id in the user state dict,
        this will never be called, which is necessary if
        the system users are not on the Hub system (i.e. Hub itself is in a container).
        """
        import pwd
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

    def start(self, *, image=None, extra_create_kwargs=None,
        extra_host_config=None):
        """start the single-user server in a docker container"""
        if image:
            self.log.warning("Specifying image via .start args is deprecated")
            self.image = image
        if extra_create_kwargs:
            self.log.warning("Specifying extra_create_kwargs via .start args is deprecated")
            self.extra_create_kwargs.update(extra_create_kwargs)
        if extra_host_config:
            self.log.warning("Specifying extra_host_config via .start kwargs is deprecated")
            self.extra_host_config.update(extra_host_config)

        self.extra_create_kwargs.setdefault('working_dir', self.homedir)
        # systemuser image must be started as root
        # relies on NB_UID and NB_USER handling in docker-stacks
        self.extra_create_kwargs.setdefault('user', '0')

        return super(SystemUserSpawner, self).start()
