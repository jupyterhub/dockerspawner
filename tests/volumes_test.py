"""Test volume manipulation logic
"""
from __future__ import absolute_import, division, print_function

import types
import pytest
from traitlets.config import LoggingConfigurable


def test_binds(monkeypatch):
    import jupyterhub
    monkeypatch.setattr("jupyterhub.spawner.Spawner", _MockSpawner)
    from dockerspawner.dockerspawner import DockerSpawner
    d = DockerSpawner()
    d.user = types.SimpleNamespace(name='xyz')
    d.volumes = {
        'a': 'b',
        'c': {'bind': 'd', 'mode': 'Z'},
    }
    assert d.volume_binds == {
        'a': {'bind': 'b', 'mode': 'rw'},
        'c': {'bind': 'd', 'mode': 'Z'},
    }
    d.volumes = {'a': 'b', 'c': 'd', 'e': 'f'}
    assert d.volume_mount_points == ['b', 'd', 'f']
    d.volumes = {'/nfs/{username}': {'bind': '/home/{username}', 'mode': 'z'}}
    assert d.volume_binds == {'/nfs/xyz': {'bind': '/home/xyz', 'mode': 'z'}}
    assert d.volume_mount_points == ['/home/xyz']

def test_slugify(monkeypatch):
    import jupyterhub
    monkeypatch.setattr("jupyterhub.spawner.Spawner", _MockSpawner)
    from dockerspawner.dockerspawner import DockerSpawner
    d = DockerSpawner()
    d.user = types.SimpleNamespace(name='s! me')
    d.volumes = {'/opt/notebooks/{username}': '/home/jovyan/'}
    print(d.volume_binds['/opt/notebooks/s-me'])
    assert d.volume_binds['/opt/notebooks/s-me'] == {'bind': '/home/jovyan/', 'mode': 'rw'}



class _MockSpawner(LoggingConfigurable):
    pass
