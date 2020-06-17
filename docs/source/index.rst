.. DockerSpawner documentation master file, created by
   sphinx-quickstart on Wed Jun 17 11:32:33 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============
DockerSpawner
=============

The **dockerspawner** (also known as JupyterHub Docker Spawner), enables
`JupyterHub <https://github.com/jupyterhub/jupyterhub>`_ to spawn single user
notebook servers in `Docker containers <https://www.docker.com/resources/what-container>`_.

There are three basic types of spawners available for dockerspawner:

- DockerSpawner: takes an authenticated user and spawns a notebook server
  in a Docker container for the user.
- SwarmSpawner: launches single user notebook servers as Docker Swarm mode
  services.
- SystemUserSpawner: spawns single user notebook servers
  that correspond to system users.


Contents
========

Installation Guide
------------------
.. toctree::
   :maxdepth: 2

   install

Choosing a spawner
------------------
.. toctree::
   :maxdepth: 3

   spawner-types

Data persistence
----------------
.. toctree::
   :maxdepth: 2

   data-persistence

Picking or building a Docker image
----------------------------------
.. toctree::
   :maxdepth: 2

   docker-image

Contributing
------------
.. toctree::
   :maxdepth: 2

   contributing

API Reference
-------------

.. toctree::
   :maxdepth: 2

   api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
