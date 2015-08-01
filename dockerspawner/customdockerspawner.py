import pwd

from dockerspawner import DockerSpawner
from textwrap import dedent
from traitlets import (
    Integer,
    Unicode,
)
from tornado import gen

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
        git_version = yield self.git('version')
        print('git version' + git_version)
        yield super(CustomDockerSpawner, self).start(
            image=image
        )

    def _env_default(self):
        env = super(CustomDockerSpawner, self)._env_default()

        print("User object stuff")
        print(self.user)
        env.update({'JPY_GITHUBURL': _GITHUBURL})

        return env
