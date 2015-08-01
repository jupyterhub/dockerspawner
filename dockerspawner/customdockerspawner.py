import pwd
from tempfile import mkdtemp
from datetime import timedelta

from dockerspawner import DockerSpawner
from textwrap import dedent
from traitlets import (
    Integer,
    Unicode,
)
from tornado import gen

from escapism import escape

import git


class CustomDockerSpawner(DockerSpawner):
    def __init__(self, **kwargs):
        self.repo_url = kwargs['repo']
        self.repo_sha = kwargs.get('last_commit', '')
        super(CustomDockerSpawner, self).__init__(**kwargs)

    _git_executor = None
    @property
    def git_executor(self):
        """single global git executor"""
        cls = self.__class__
        if cls._git_executor is None:
            cls._git_executor = ThreadPoolExecutor(1)
        return cls._git_executor

    _git_client = None
    @property
    def git_client(self):
        """single global git client instance"""
        cls = self.__class__
        if cls._git_client is None:
            cls._git_client = git.Git()
        return cls._git_client

    def _git(self, method, *args, **kwargs):
        """wrapper for calling git methods
        
        to be passed to ThreadPoolExecutor
        """
        m = getattr(self.git_client, method)
        return m(*args, **kwargs)

    def git(self, method, *args, **kwargs):
        """Call a git method in a background thread
        
        returns a Future
        """
        return self.executor.submit(self._git, method, *args, **kwargs)

    def get_state(self):
        return {} #state = super(DockerSpawner, self).get_state()

    _escaped_repo_url = None
    @property
    def escaped_repo_url(self):
        if self._escaped_repo_url is None:
            trans = str.maketrans(':/-.', "____")
            self._escaped_repo_url = self.repo_url.translate(trans)
        return self._escaped_repo_url

    @property
    def container_name(self):
        return "{}-{}-{}-{}".format(self.container_prefix,
                                    self.escaped_name,
                                    self.escaped_repo_url,
                                    self.repo_sha)

    @gen.coroutine
    def start(self, image=None):
        """start the single-user server in a docker container"""
        tmp_dir = mkdtemp(suffix='everware')
        yield self.git('clone', self.repo_url, tmp_dir)
        # is this blocking?
        # use the username, git repo URL and HEAD commit sha to derive
        # the image name
        repo = git.Repo(tmp_dir)
        self.repo_sha = repo.rev_parse("HEAD")

        image_name = "everware/{}-{}-{}".format(self.user.name,
                                                self.escaped_repo_url,
                                                self.repo_sha)
        self.log.debug("Building image {}".format(image_name))
        build_log = yield gen.with_timeout(timedelta(30),
                                           self.docker('build',
                                                       path=tmp_dir,
                                                       tag=image_name,
                                                       rm=True)
        )
        self.log.debug("".join(str(line) for line in build_log))
        self.log.info("Built docker image {}".format(image_name))

        images = yield self.docker('images', image_name)
        self.log.debug(images)

        yield super(CustomDockerSpawner, self).start(
            image=image_name
        )

    def _env_default(self):
        env = super(CustomDockerSpawner, self)._env_default()

        env.update({'JPY_GITHUBURL': self.repo_url})

        return env
