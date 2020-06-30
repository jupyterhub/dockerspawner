import logging
import pytest

from traitlets.config import Config
from tornado import web

from dockerspawner import DockerSpawner


def test_deprecated_config(caplog):
    cfg = Config()
    cfg.DockerSpawner.image_whitelist = {"1.0": "jupyterhub/singleuser:1.0"}

    log = logging.getLogger("testlog")
    spawner = DockerSpawner(config=cfg, log=log)
    assert caplog.record_tuples == [
        (
            log.name,
            logging.WARNING,
            'DockerSpawner.image_whitelist is deprecated in DockerSpawner 0.12.0, use '
            'DockerSpawner.allowed_images instead',
        )
    ]

    assert spawner.allowed_images == {"1.0": "jupyterhub/singleuser:1.0"}


def test_deprecated_methods():
    cfg = Config()
    cfg.DockerSpawner.image_whitelist = {"1.0": "jupyterhub/singleuser:1.0"}
    spawner = DockerSpawner(config=cfg)

    assert spawner.check_allowed("1.0")
    with pytest.deprecated_call():
        assert spawner.check_image_whitelist("1.0")
