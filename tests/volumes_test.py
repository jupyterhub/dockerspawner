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

def test_volume_naming_configuration(monkeypatch):
    from dockerspawner.dockerspawner import DockerSpawner
    d = DockerSpawner()
    d.user = types.SimpleNamespace(name='joe')
    d.volumes = {'data/{username}': {'bind': '/home/{username}', 'mode': 'z'}}

    def test_format(label_template, spawner):
        return "THIS IS A TEST"

    d.format_volume_name = test_format
    assert d.volume_binds == {'THIS IS A TEST':{'bind': 'THIS IS A TEST', 'mode': 'z'}}
    assert d.volume_mount_points == ['THIS IS A TEST']

def test_default_format_volume_name(monkeypatch):
    from dockerspawner.dockerspawner import DockerSpawner
    d = DockerSpawner()
    d.user = types.SimpleNamespace(name='user@email.com')
    d.volumes = {'data/{username}': {'bind': '/home/{username}', 'mode': 'z'}}
    assert d.volume_binds == {'data/user@email.com':{'bind': '/home/user@email.com', 'mode': 'z'}}
    assert d.volume_mount_points == ['/home/user@email.com']

def test_escaped_format_volume_name(monkeypatch):
    import dockerspawner
    from dockerspawner import DockerSpawner

    d = DockerSpawner()
    d.user = types.SimpleNamespace(name='user@email.com')
    d.volumes = {'data/{username}': {'bind': '/home/{username}', 'mode': 'z'}}
    d.format_volume_name = dockerspawner.volumenamingstrategy.escaped_format_volume_name
    assert d.volume_binds == {'data/user_40email_2Ecom':{'bind': '/home/user_40email_2Ecom', 'mode': 'z'}}
    assert d.volume_mount_points == ['/home/user_40email_2Ecom']

class _MockSpawner(LoggingConfigurable):
    pass
