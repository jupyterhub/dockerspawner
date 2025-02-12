# Changes in DockerSpawner

For detailed changes from the prior release, click on the version number, and
its link will bring up a GitHub listing of changes. Use `git log` on the
command line for details.

## [Unreleased]

## 14

### 14.0.0 2024-02-12

14.0.0 is a small release.
It is designated a major revision because it drops support for Python < 3.9 and JupyterHub < 4.

([full changelog](https://github.com/jupyterhub/dockerspawner/compare/13.0.0...14.0.0))

#### API and Breaking Changes

- require Python 3.9, jupyterhub 4, unpin pytest-asyncio [#530](https://github.com/jupyterhub/dockerspawner/pull/530) ([@minrk](https://github.com/minrk))

#### New features added

- support for bind propagation [#526](https://github.com/jupyterhub/dockerspawner/pull/526) ([@jannefleischer](https://github.com/jannefleischer), [@minrk](https://github.com/minrk))

#### Enhancements made

- compact debug log into single line [#521](https://github.com/jupyterhub/dockerspawner/pull/521) ([@haobibo](https://github.com/haobibo), [@minrk](https://github.com/minrk))

#### Bugs fixed

- Support options_from_form config [#525](https://github.com/jupyterhub/dockerspawner/pull/525) ([@akhmerov](https://github.com/akhmerov), [@minrk](https://github.com/minrk))

#### Maintenance and upkeep improvements

- update some test dependencies [#531](https://github.com/jupyterhub/dockerspawner/pull/531) ([@minrk](https://github.com/minrk))
- update test versions in ci [#529](https://github.com/jupyterhub/dockerspawner/pull/529) ([@minrk](https://github.com/minrk))
- update internal-ssl test for current docker compose [#527](https://github.com/jupyterhub/dockerspawner/pull/527) ([@minrk](https://github.com/minrk))

#### Documentation improvements

- Document c.DockerSpawner.mounts [#510](https://github.com/jupyterhub/dockerspawner/pull/510) ([@zhangnew](https://github.com/zhangnew), [@minrk](https://github.com/minrk))

#### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/jupyterhub/dockerspawner/graphs/contributors?from=2023-11-21&to=2025-02-12&type=c))

@akhmerov ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Aakhmerov+updated%3A2023-11-21..2025-02-12&type=Issues)) | @consideRatio ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3AconsideRatio+updated%3A2023-11-21..2025-02-12&type=Issues)) | @haobibo ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ahaobibo+updated%3A2023-11-21..2025-02-12&type=Issues)) | @jannefleischer ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ajannefleischer+updated%3A2023-11-21..2025-02-12&type=Issues)) | @manics ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Amanics+updated%3A2023-11-21..2025-02-12&type=Issues)) | @minrk ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Aminrk+updated%3A2023-11-21..2025-02-12&type=Issues)) | @yuvipanda ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ayuvipanda+updated%3A2023-11-21..2025-02-12&type=Issues)) | @zhangnew ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Azhangnew+updated%3A2023-11-21..2025-02-12&type=Issues))

## 13

### [13.0] 2023-11-21

([full changelog](https://github.com/jupyterhub/dockerspawner/compare/12.1.0...13.0.0))

13.0 Fixes security vulnerability GHSA-hfgr-h3vc-p6c2, which allowed authenticated users to spawn arbitrary images
unless `DockerSpawner.allowed_images` was specified.

#### API and Breaking Changes

- Add and require `DockerSpawner.allowed_images='*'` to allow any image to be spawned via `user_options`. (GHSA-hfgr-h3vc-p6c2)
- Remove deprecated, broken hub_ip_connect [#499](https://github.com/jupyterhub/dockerspawner/pull/499) ([@minrk](https://github.com/minrk))
- Require python 3.8+ and jupyterhub 2.3.1+ [#488](https://github.com/jupyterhub/dockerspawner/pull/488) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))

#### New features added

- Switch default image to quay.io [#504](https://github.com/jupyterhub/dockerspawner/pull/504) ([@yuvipanda](https://github.com/yuvipanda), [@minrk](https://github.com/minrk), [@manics](https://github.com/manics))
- allow extra_host_config and extra_create_kwargs to be callable [#500](https://github.com/jupyterhub/dockerspawner/pull/500) ([@minrk](https://github.com/minrk))

#### Enhancements made

- Merge host config/create_kwargs [#501](https://github.com/jupyterhub/dockerspawner/pull/501) ([@minrk](https://github.com/minrk))

#### Bugs fixed

- update object_name with current image [#466](https://github.com/jupyterhub/dockerspawner/pull/466) ([@floriandeboissieu](https://github.com/floriandeboissieu), [@minrk](https://github.com/minrk))
- Fix imagename not to include letter ':' [#464](https://github.com/jupyterhub/dockerspawner/pull/464) ([@yamaton](https://github.com/yamaton), [@minrk](https://github.com/minrk))
- clear object_id when removing object [#447](https://github.com/jupyterhub/dockerspawner/pull/447) ([@minrk](https://github.com/minrk), [@manics](https://github.com/manics))

#### Maintenance and upkeep improvements

- pre-commit: add pyupgrade and autoflake, simplify flake8 config [#489](https://github.com/jupyterhub/dockerspawner/pull/489) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Require python 3.8+ and jupyterhub 2.3.1+ [#488](https://github.com/jupyterhub/dockerspawner/pull/488) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Add dependabot.yaml to bump github actions [#487](https://github.com/jupyterhub/dockerspawner/pull/487) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Update release workflow and RELEASE.md, set version with tbump [#486](https://github.com/jupyterhub/dockerspawner/pull/486) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Refresh test workflow and associated config, accept podmain test failure for now [#485](https://github.com/jupyterhub/dockerspawner/pull/485) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))
- Use python 3.11 on RTD [#482](https://github.com/jupyterhub/dockerspawner/pull/482) ([@minrk](https://github.com/minrk))
- Add test strategy for JupyterHub v3.1.1 [#479](https://github.com/jupyterhub/dockerspawner/pull/479) ([@Sheila-nk](https://github.com/Sheila-nk), [@GeorgianaElena](https://github.com/GeorgianaElena), [@minrk](https://github.com/minrk))
- test options_form and escape [#468](https://github.com/jupyterhub/dockerspawner/pull/468) ([@Sheila-nk](https://github.com/Sheila-nk), [@minrk](https://github.com/minrk))
- test callable allowed_images and host_ip [#467](https://github.com/jupyterhub/dockerspawner/pull/467) ([@Sheila-nk](https://github.com/Sheila-nk), [@minrk](https://github.com/minrk))
- Test jupyterhub2 [#443](https://github.com/jupyterhub/dockerspawner/pull/443) ([@manics](https://github.com/manics), [@minrk](https://github.com/minrk))

#### Documentation improvements

- Add extra_create_kwargs example, plus docs readability improvements [#493](https://github.com/jupyterhub/dockerspawner/pull/493) ([@matthewwiese](https://github.com/matthewwiese), [@manics](https://github.com/manics))
- update versions in swarm example [#454](https://github.com/jupyterhub/dockerspawner/pull/454) ([@minrk](https://github.com/minrk), [@GeorgianaElena](https://github.com/GeorgianaElena))
- add generate-certs service to internal-ssl example [#446](https://github.com/jupyterhub/dockerspawner/pull/446) ([@minrk](https://github.com/minrk), [@manics](https://github.com/manics))
- Add Podman to docs [#444](https://github.com/jupyterhub/dockerspawner/pull/444) ([@manics](https://github.com/manics), [@minrk](https://github.com/minrk))

#### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/jupyterhub/dockerspawner/graphs/contributors?from=2021-07-22&to=2023-11-20&type=c))

@consideRatio ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3AconsideRatio+updated%3A2021-07-22..2023-11-20&type=Issues)) | @floriandeboissieu ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Afloriandeboissieu+updated%3A2021-07-22..2023-11-20&type=Issues)) | @gatoniel ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Agatoniel+updated%3A2021-07-22..2023-11-20&type=Issues)) | @GeorgianaElena ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3AGeorgianaElena+updated%3A2021-07-22..2023-11-20&type=Issues)) | @manics ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Amanics+updated%3A2021-07-22..2023-11-20&type=Issues)) | @matthewwiese ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Amatthewwiese+updated%3A2021-07-22..2023-11-20&type=Issues)) | @minrk ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Aminrk+updated%3A2021-07-22..2023-11-20&type=Issues)) | @Sheila-nk ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3ASheila-nk+updated%3A2021-07-22..2023-11-20&type=Issues)) | @yamaton ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ayamaton+updated%3A2021-07-22..2023-11-20&type=Issues)) | @yuvipanda ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ayuvipanda+updated%3A2021-07-22..2023-11-20&type=Issues))

## 12

### [12.1] 2021-07-22

([full changelog](https://github.com/jupyterhub/dockerspawner/compare/12.0.0...12.1.0))

#### Enhancements made

- support cpu limit via cpu_quota / cpu_period [#435](https://github.com/jupyterhub/dockerspawner/pull/435) ([@minrk](https://github.com/minrk))
- Log post_start exec output [#427](https://github.com/jupyterhub/dockerspawner/pull/427) ([@minrk](https://github.com/minrk))
- Allow to specify a callable for `mem_limit` [#420](https://github.com/jupyterhub/dockerspawner/pull/420) ([@zeehio](https://github.com/zeehio))

#### Maintenance and upkeep improvements

- update release steps for main branch [#434](https://github.com/jupyterhub/dockerspawner/pull/434) ([@minrk](https://github.com/minrk))
- more debug info from docker when tests fail [#433](https://github.com/jupyterhub/dockerspawner/pull/433) ([@minrk](https://github.com/minrk))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/dockerspawner/graphs/contributors?from=2021-03-26&to=2021-07-19&type=c))

[@1kastner](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3A1kastner+updated%3A2021-03-26..2021-07-19&type=Issues) | [@manics](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Amanics+updated%3A2021-03-26..2021-07-19&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Aminrk+updated%3A2021-03-26..2021-07-19&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Awelcome+updated%3A2021-03-26..2021-07-19&type=Issues) | [@zeehio](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Azeehio+updated%3A2021-03-26..2021-07-19&type=Issues)

### [12.0] 2021-03-26

This is a big release!

Several bugs have been fixed, especially in SwarmSpawner, and more configuration options added.

#### New escaping scheme

In particular, the biggest backward-incompatible change to highlight
is the container (and volume) name escaping scheme now produces DNS-safe results, which matches the behavior of kubespawner.
This is a stricter subset of characters than docker containers strictly require,
but many features don't work right without it.
The result is for certain user names and/or server names, their container and/or volume names will change.
Upgrading existing deployments will result in disconnecting these users from their running containers and volumes, which means:

- if there are running users across the upgrade,
  some containers will need to be manually stopped
- some volumes may need to be renamed, which [docker doesn't support](https://github.com/moby/moby/issues/31154),
  but [can be done](https://github.com/moby/moby/issues/31154#issuecomment-360531460):

  ```bash
  docker volume create --name $new_volume
  docker run --rm -it -v $old_volume:/from -v $new_volume:/to alpine ash -c "cd /from ; cp -av . /to"
  docker volume rm $old_volume
  ```

The main differences are:

- The escape character is `-` instead of `_` which means `-` cannot itself be a safe character and must be escaped to `-2d`
- Uppercase characters are now escaped (normalizing to lowercase at the username level is common)

So affected usernames are those with `-` or uppercase letters, or any that already needed escaping.

You can restore the pre-12.0 behavior with:

```python
c.DockerSpawner.escape = "legacy"
```

#### SystemUserSpawner.run_as_root

Another security-related change is the addition of `SystemUserSpawner.run_as_root`.
Prior to 12.0, SystemUserSpawner always ran as root and relied on the container to use $NB_USER and $NB_UID to "become" the user.
This behavior meant that user containers based on images that lacked this behavior would all run as root.
To address this, `run_as_root` behavior is now opt-in

All changes are detailed below.

([full changelog](https://github.com/jupyterhub/dockerspawner/compare/0.11.1...12.0.0))

#### New features added

- apply template formatting to all of extra_create_kwargs, extra_host_config [#409](https://github.com/jupyterhub/dockerspawner/pull/409) ([@minrk](https://github.com/minrk))
- Add mounts option for more advanced binds [#406](https://github.com/jupyterhub/dockerspawner/pull/406) ([@minrk](https://github.com/minrk))
- Add JUPYTER_IMAGE_SPEC to env. [#316](https://github.com/jupyterhub/dockerspawner/pull/316) ([@danielballan](https://github.com/danielballan))
- Added post_start_cmd [#307](https://github.com/jupyterhub/dockerspawner/pull/307) ([@mohirio](https://github.com/mohirio))

#### Enhancements made

- Use default cmd=None to indicate using the image command [#415](https://github.com/jupyterhub/dockerspawner/pull/415) ([@minrk](https://github.com/minrk))
- add 'skip' option for pull_policy [#411](https://github.com/jupyterhub/dockerspawner/pull/411) ([@minrk](https://github.com/minrk))
- Add auto_remove to host_config [#318](https://github.com/jupyterhub/dockerspawner/pull/318) ([@jtpio](https://github.com/jtpio))
- Make default name_template compatible with named servers. [#315](https://github.com/jupyterhub/dockerspawner/pull/315) ([@danielballan](https://github.com/danielballan))
- SystemUserSpawner: Pass group id to the container [#304](https://github.com/jupyterhub/dockerspawner/pull/304) ([@zeehio](https://github.com/zeehio))
- Allow lookup of host homedir via `pwd` [#302](https://github.com/jupyterhub/dockerspawner/pull/302) ([@AdrianoKF](https://github.com/AdrianoKF))

#### Bugs fixed

- (PATCH) SwarmSpawner, InvalidArgument: Incompatible options have been provided for the bind type mount. [#419](https://github.com/jupyterhub/dockerspawner/pull/419) ([@cmotadev](https://github.com/cmotadev))
- Make sure that create_object() creates the service task [#396](https://github.com/jupyterhub/dockerspawner/pull/396) ([@girgink](https://github.com/girgink))
- avoid name collisions when using named servers [#386](https://github.com/jupyterhub/dockerspawner/pull/386) ([@minrk](https://github.com/minrk))
- Fix issue with pulling images from custom repos that contain a port [#334](https://github.com/jupyterhub/dockerspawner/pull/334) ([@raethlein](https://github.com/raethlein))

#### Maintenance and upkeep improvements

- async/await [#417](https://github.com/jupyterhub/dockerspawner/pull/417) ([@minrk](https://github.com/minrk))
- stop building docs on circleci [#387](https://github.com/jupyterhub/dockerspawner/pull/387) ([@minrk](https://github.com/minrk))
- Test with latest jh [#379](https://github.com/jupyterhub/dockerspawner/pull/379) ([@GeorgianaElena](https://github.com/GeorgianaElena))
- Fix RTD build [#378](https://github.com/jupyterhub/dockerspawner/pull/378) ([@GeorgianaElena](https://github.com/GeorgianaElena))
- Add release instructions and Travis deploy [#377](https://github.com/jupyterhub/dockerspawner/pull/377) ([@GeorgianaElena](https://github.com/GeorgianaElena))
- Fix tests [#374](https://github.com/jupyterhub/dockerspawner/pull/374) ([@GeorgianaElena](https://github.com/GeorgianaElena))
- Add README badges [#356](https://github.com/jupyterhub/dockerspawner/pull/356) ([@GeorgianaElena](https://github.com/GeorgianaElena))

#### Documentation improvements

- Update swarm example [#418](https://github.com/jupyterhub/dockerspawner/pull/418) ([@minrk](https://github.com/minrk))
- improve robustness of internal-ssl example [#416](https://github.com/jupyterhub/dockerspawner/pull/416) ([@minrk](https://github.com/minrk))
- update versions in docker-image docs [#410](https://github.com/jupyterhub/dockerspawner/pull/410) ([@minrk](https://github.com/minrk))
- Add GitHub Action readme badge [#408](https://github.com/jupyterhub/dockerspawner/pull/408) ([@consideRatio](https://github.com/consideRatio))
- Switch CI to GitHub actions [#407](https://github.com/jupyterhub/dockerspawner/pull/407) ([@minrk](https://github.com/minrk))
- touch up simple example [#405](https://github.com/jupyterhub/dockerspawner/pull/405) ([@minrk](https://github.com/minrk))
- add example for selecting arbitrary image via options_form [#401](https://github.com/jupyterhub/dockerspawner/pull/401) ([@minrk](https://github.com/minrk))
- Typo fix in the docs [#380](https://github.com/jupyterhub/dockerspawner/pull/380) ([@jtpio](https://github.com/jtpio))
- Add docs [#375](https://github.com/jupyterhub/dockerspawner/pull/375) ([@GeorgianaElena](https://github.com/GeorgianaElena))
- Fix dead link in doc [#350](https://github.com/jupyterhub/dockerspawner/pull/350) ([@JocelynDelalande](https://github.com/JocelynDelalande))
- Fix project name typo [#339](https://github.com/jupyterhub/dockerspawner/pull/339) ([@kinow](https://github.com/kinow))

#### API and Breaking Changes

- Make escaping DNS-safe [#414](https://github.com/jupyterhub/dockerspawner/pull/414) ([@minrk](https://github.com/minrk))
- add SystemUserSpawner.run_as_root [#412](https://github.com/jupyterhub/dockerspawner/pull/412) ([@minrk](https://github.com/minrk))
- Rename DockerSpawner.image_whitelist to allowed_images [#381](https://github.com/jupyterhub/dockerspawner/pull/381) ([@GeorgianaElena](https://github.com/GeorgianaElena))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/dockerspawner/graphs/contributors?from=2019-04-25&to=2021-03-24&type=c))

[@1kastner](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3A1kastner+updated%3A2019-04-25..2021-03-24&type=Issues) | [@AdrianoKF](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3AAdrianoKF+updated%3A2019-04-25..2021-03-24&type=Issues) | [@anmtan](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Aanmtan+updated%3A2019-04-25..2021-03-24&type=Issues) | [@AnubhavUjjawal](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3AAnubhavUjjawal+updated%3A2019-04-25..2021-03-24&type=Issues) | [@belfhi](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Abelfhi+updated%3A2019-04-25..2021-03-24&type=Issues) | [@bellackn](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Abellackn+updated%3A2019-04-25..2021-03-24&type=Issues) | [@bjornandre](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Abjornandre+updated%3A2019-04-25..2021-03-24&type=Issues) | [@blacksailer](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ablacksailer+updated%3A2019-04-25..2021-03-24&type=Issues) | [@cblomart](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Acblomart+updated%3A2019-04-25..2021-03-24&type=Issues) | [@choldgraf](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Acholdgraf+updated%3A2019-04-25..2021-03-24&type=Issues) | [@cmotadev](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Acmotadev+updated%3A2019-04-25..2021-03-24&type=Issues) | [@cmseal](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Acmseal+updated%3A2019-04-25..2021-03-24&type=Issues) | [@co60ca](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Aco60ca+updated%3A2019-04-25..2021-03-24&type=Issues) | [@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3AconsideRatio+updated%3A2019-04-25..2021-03-24&type=Issues) | [@cyliu0204](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Acyliu0204+updated%3A2019-04-25..2021-03-24&type=Issues) | [@danielballan](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Adanielballan+updated%3A2019-04-25..2021-03-24&type=Issues) | [@danlester](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Adanlester+updated%3A2019-04-25..2021-03-24&type=Issues) | [@efagerberg](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Aefagerberg+updated%3A2019-04-25..2021-03-24&type=Issues) | [@gatoniel](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Agatoniel+updated%3A2019-04-25..2021-03-24&type=Issues) | [@GeorgianaElena](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3AGeorgianaElena+updated%3A2019-04-25..2021-03-24&type=Issues) | [@girgink](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Agirgink+updated%3A2019-04-25..2021-03-24&type=Issues) | [@hugoJuhel](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3AhugoJuhel+updated%3A2019-04-25..2021-03-24&type=Issues) | [@jameholme](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ajameholme+updated%3A2019-04-25..2021-03-24&type=Issues) | [@jamesdbrock](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ajamesdbrock+updated%3A2019-04-25..2021-03-24&type=Issues) | [@JocelynDelalande](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3AJocelynDelalande+updated%3A2019-04-25..2021-03-24&type=Issues) | [@jtpio](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ajtpio+updated%3A2019-04-25..2021-03-24&type=Issues) | [@kinow](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Akinow+updated%3A2019-04-25..2021-03-24&type=Issues) | [@kkr78](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Akkr78+updated%3A2019-04-25..2021-03-24&type=Issues) | [@ltupin](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Altupin+updated%3A2019-04-25..2021-03-24&type=Issues) | [@manics](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Amanics+updated%3A2019-04-25..2021-03-24&type=Issues) | [@mathematicalmichael](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Amathematicalmichael+updated%3A2019-04-25..2021-03-24&type=Issues) | [@meeseeksmachine](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ameeseeksmachine+updated%3A2019-04-25..2021-03-24&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Aminrk+updated%3A2019-04-25..2021-03-24&type=Issues) | [@missingcharacter](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Amissingcharacter+updated%3A2019-04-25..2021-03-24&type=Issues) | [@mohirio](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Amohirio+updated%3A2019-04-25..2021-03-24&type=Issues) | [@myurasov](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Amyurasov+updated%3A2019-04-25..2021-03-24&type=Issues) | [@nazeels](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Anazeels+updated%3A2019-04-25..2021-03-24&type=Issues) | [@nmvega](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Anmvega+updated%3A2019-04-25..2021-03-24&type=Issues) | [@nuraym](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Anuraym+updated%3A2019-04-25..2021-03-24&type=Issues) | [@parente](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Aparente+updated%3A2019-04-25..2021-03-24&type=Issues) | [@raethlein](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Araethlein+updated%3A2019-04-25..2021-03-24&type=Issues) | [@sabuhish](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Asabuhish+updated%3A2019-04-25..2021-03-24&type=Issues) | [@sangramga](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Asangramga+updated%3A2019-04-25..2021-03-24&type=Issues) | [@support](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Asupport+updated%3A2019-04-25..2021-03-24&type=Issues) | [@TimoRoth](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3ATimoRoth+updated%3A2019-04-25..2021-03-24&type=Issues) | [@vlizanae](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Avlizanae+updated%3A2019-04-25..2021-03-24&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Awelcome+updated%3A2019-04-25..2021-03-24&type=Issues) | [@Wildcarde](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3AWildcarde+updated%3A2019-04-25..2021-03-24&type=Issues) | [@willingc](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Awillingc+updated%3A2019-04-25..2021-03-24&type=Issues) | [@wwj718](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Awwj718+updated%3A2019-04-25..2021-03-24&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Ayuvipanda+updated%3A2019-04-25..2021-03-24&type=Issues) | [@z3ky](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Az3ky+updated%3A2019-04-25..2021-03-24&type=Issues) | [@zeehio](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Azeehio+updated%3A2019-04-25..2021-03-24&type=Issues) | [@zhiyuli](https://github.com/search?q=repo%3Ajupyterhub%2Fdockerspawner+involves%3Azhiyuli+updated%3A2019-04-25..2021-03-24&type=Issues)

## 0.11

### [0.11.1] - 2019-04-25

- Fix some compatibility issues
- Add more states to be recognized as pending for SwarmSpawner

### [0.11.0] - 2019-03-01

#### New features:

- Support selecting docker spawner via JupyterHub 1.0's entrypoints:

  ```python
  c.JupyterHub.spawner_class = 'docker' # or 'docker-swarm' or 'docker-system-user'
  ```

- Support total internal SSL encryption with JupyterHub 1.0
- Add new `DockerSpawner.pull_policy` to configure pulling of images.
  Values are inspired by Kubernetes, and case-insensitive. Can be any of
  "IfNotPresent" (new default), "Always", and "Never" (pre-0.11 behavior).
  Now the image will be pulled by default if it is not present.
- Add `image_whitelist` configuration which, if set, defines a default options
  form for users to pick the desired image.
  `image_whitelist` is a dict of `{'descriptive key': 'image:tag'}`.
- Add `SwarmSpawner.extra_placement_spec` configuration for setting service placement

#### Fixes:

- Slow startup in SwarmSpawner could be treated as failures.

## 0.10

### [0.10.0] - 2018-09-03

- Add `dockerspawner.SwarmSpawner` for spawning with Docker Swarm
- Removed deprecated `extra_start_kwargs`
- `host_ip` is configurable
- Added `container_name_template` configuration for custom container naming

## 0.9

### [0.9.1] - 2017-08-23

- Fix typo which would cause using the deprecated `.hub_ip_connect` configuration
  with JupyterHub 0.8 to crash instead of warn in 0.9.0.

### [0.9.0] - 2017-08-20

0.9 cleans up some configuration and improves support for the transition from JupyterHub 0.8 to 0.9.
It also reduces some of the special arguments and env handling,
allowing for more consistency with other Spawners,
and fewer assumptions about the image that will be used by the Spawner.

The following is a minimal Dockerfile that works with DockerSpawner 0.9 and JupyterHub 0.7.2:

```Dockerfile
FROM python:3.6
RUN pip install \
    jupyterhub==0.8.0 \
    'notebook==5.0.0'

# Don't want to run as root!
RUN useradd -m jovyan
ENV HOME=/home/jovyan
WORKDIR $HOME
USER jovyan

CMD ["jupyterhub-singleuser"]
```

In particular:

- any image with the correct version of JupyterHub installed (it should match JupyterHub) should work with DockerSpawner.
- any image **based on one of the [jupyter/docker-stacks][]** should work with SystemUserSpawner.
  There is no longer any need for the `jupyterhub/systemuser` docker image.
- The jupyterhub/singleuser image is now built from the JupyterHub repo, not this one.
- `jupyterhub/systemuser` image is deprecated.
  `jupyterhub/systemuser` launches containers as root and relies on
  the `NB_UID` and `NB_GID` handling of `jupyter/docker-stacks` to setup the user.
- The default `jupyterhub/singleuser` image has tags for JupyterHub versions,
  to ensure image compatibility with JupyterHub.
  The default image is now `jupyterhub/singleuser:x.y`, where `x.y` is the major.minor version of
  the current JupyterHub instance,
  so DockerSpawner should work by default with JupyterHub 0.7 or 0.8
  without needing to specify the image.
- `Spawner.cmd` config is now supported, which can be used to override the CMD arg.
  By default, the image's CMD is used.
- `Spawner.get_args()` behavior is now properly inherited,
  and args are appended to the spawn command as in other Spawners.
- Arguments are now passed via `.get_args()` as in the base Spawner,
  rather than custom environment variables which user images had to support.
- `DockerSpawner.hub_ip_connect` is deprecated when running with JupyterHub 0.8.
  Use `JupyterHub.hub_connect_ip` instead, which is used by all Spawners.

Some configuration has been cleaned up to be clearer and more concise:

- `DockerSpawner.container_image` is deprecated in favor of `DockerSpawner.image`.
- `DockerSpawner.container_port` is deprecated in favor of existing `Spawner.port`.
- Inaccurately named `DockerSpawner.container_ip` is deprecated in favor of `DockerSpawner.host_ip`
  because it configures the host IP forwarded to the container.

[jupyter/docker-stacks]: https://github.com/jupyter/docker-stacks

## [0.8] - 2017-07-28

- experimental fixes for running on Windows
- added `DockerSpawner.client_kwargs` config to passthrough to the `docker.Client` constructor
- workaround bug where Docker can report ports as strings
- bump docker dependency to new `docker` package from `docker-py`

## [0.7] - 2017-03-14

- Only need to set `DockerSpawner.network_name` to run on a docker network,
  instead of setting `host_config`, `network_name`, and `use_internal_ip` separately.
- Set `mem_limit` on `host_config` for docker API 1.19
- Match start keyword args on SystemUserSpawner to DockerSpawner

## [0.6] - 2017-01-02

- Add `DockerSpawner.format_volume_name` for custom naming strategies for mounted volumes.
- Support `mem_limit` config introduced in JupyterHub 0.7.
- Support `will_resume` flag necessary for resuming containers with
  `DockerSpawner.remove_containers = False` and JupyterHub 0.7
  (requires JupyterHub 0.7.1).

## [0.5] - 2016-10-05

- return ip, port from `DockerSpawner.start`, for future-compatibility (setting ip, port directly is deprecated in JupyterHub 0.7).
- Support `{username}` in volume_mounts

## [0.4] - 2016-06-07

- get singleuser script from jupyterhub 0.6.1 (0.7 will require jupyterhub package to run singleuser script)
- `get_ip_and_port()` is a tornado coroutine, rather than an asyncio coroutine, for consistency with the rest of the code.
- more configuration for ports and mounts

## [0.3] - 2016-04-22

- Moved to jupyterhub org (`jupyterhub/singleuser`, `jupyterhub/systemuser` on Docker)
- Add `rebase-singleuser` tool for building new single-user images on top of different bases
- Base default docker images on `jupyter/scipy-notebook` from jupyter/docker-stacks
- Fix environment setup to use `get_env` instead of `_env_default` (Needed for JupyterHub 0.5)

## [0.2] - 2016-02-16

- Add `DockerSpawner.links`
- Use HostIp from docker port output
- Make user home string template configurable

## 0.1 - 2016-02-03

First release

[unreleased]: https://github.com/jupyterhub/dockerspawner/compare/13.0.0...HEAD
[13.0]: https://github.com/jupyterhub/dockerspawner/compare/12.1.0...13.0.0
[12.1]: https://github.com/jupyterhub/dockerspawner/compare/12.0.0...12.1.0
[12.0]: https://github.com/jupyterhub/dockerspawner/compare/0.11.1...12.0.0
[0.11.1]: https://github.com/jupyterhub/dockerspawner/compare/0.11.0...0.11.1
[0.11.0]: https://github.com/jupyterhub/dockerspawner/compare/0.10.0...0.11.0
[0.10.0]: https://github.com/jupyterhub/dockerspawner/compare/0.9.1...0.10.0
[0.9.1]: https://github.com/jupyterhub/dockerspawner/compare/0.9.0...0.9.1
[0.9.0]: https://github.com/jupyterhub/dockerspawner/compare/0.8.0...0.9.0
[0.8]: https://github.com/jupyterhub/dockerspawner/compare/0.7.0...0.8.0
[0.7]: https://github.com/jupyterhub/dockerspawner/compare/0.6.0...0.7.0
[0.6]: https://github.com/jupyterhub/dockerspawner/compare/0.5.0...0.6.0
[0.5]: https://github.com/jupyterhub/dockerspawner/compare/0.4.0...0.5.0
[0.4]: https://github.com/jupyterhub/dockerspawner/compare/0.3.0...0.4.0
[0.3]: https://github.com/jupyterhub/dockerspawner/compare/0.2.0...0.3.0
[0.2]: https://github.com/jupyterhub/dockerspawner/compare/0.1.0...0.2.0
