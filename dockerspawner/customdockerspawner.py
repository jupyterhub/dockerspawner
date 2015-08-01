import pwd
from tempfile import mkdtemp

from dockerspawner import DockerSpawner
from textwrap import dedent
from traitlets import (
    Integer,
    Unicode,
)
from tornado import gen

from escapism import escape

import git

# XXX Hard code a github url for the moment
_GITHUBURL = 'https://github.com/everware/everware.git'

class CustomDockerSpawner(DockerSpawner):
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

    @gen.coroutine
    def start(self, image=None):
        """start the single-user server in a docker container"""
        tmp_dir = mkdtemp(suffix='everware')
        yield self.git('clone', _GITHUBURL, tmp_dir)
        # is this blocking?
        # use the username, git repo URL and HEAD commit sha to derive
        # the image name
        repo = git.Repo(tmp_dir)
        sha = repo.rev_parse("HEAD")

        trans = str.maketrans(':/-.', "____")
        escaped_url = _GITHUBURL.translate(trans)

        image_name = "everware/{}-{}-{}".format(self.user.name, escaped_url, sha)
        self.log.debug("Building image {}".format(image_name))
        docker_img = yield self.docker('build', path=tmp_dir, tag=image_name)
        self.log.info("Built docker image {}".format(image_name))

        images = yield self.docker('images', image_name)
        self.log.debug(images)

        yield super(CustomDockerSpawner, self).start(
            image=image_name
        )

    def _env_default(self):
        env = super(CustomDockerSpawner, self)._env_default()

        env.update({'JPY_GITHUBURL': _GITHUBURL})

        return env
