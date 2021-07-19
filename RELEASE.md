# How to make a release

`dockerspawner` is a package [available on
PyPI](https://pypi.org/project/dockerspawner/).
The PyPI release is done automatically by TravisCI when a tag
is pushed.

For you to follow along according to these instructions, you need
to have push rights to the [dockerspawner GitHub
repository](https://github.com/jupyterhub/dockerspawner).

## Steps to make a release

1. Checkout main and make sure it is up to date.

   ```bash
   ORIGIN=${ORIGIN:-origin} # set to the canonical remote, e.g. 'upstream' if 'origin' is not the official repo
   git checkout main
   git fetch $ORIGIN main
   git reset --hard $ORIGIN/main
   # WARNING! This next command deletes any untracked files in the repo
   git clean -xfd
   ```

1. Update [docs/source/changelog.md](docs/source/changelog.md) and add it to
   the working tree.

   ```bash
   git add docs/source/changelog.md
   ```

   Tip: Identifying the changes can be made easier with the help of the
   [executablebooks/github-activity](https://github.com/executablebooks/github-activity)
   utility.

1. Set the `version_info` variable in [\_version.py](dockerspawner/_version.py)
   appropriately and make a commit.

   ```bash
   git add dockerspawner/_version.py
   VERSION=...  # e.g. 1.2.3
   git commit -m "release $VERSION"
   ```

   Tip: You can get the current project version by checking the [latest
   tag on GitHub](https://github.com/jupyterhub/dockerspawner/tags).

1. Create a git tag for the release commit.

   ```bash
   git tag -a $VERSION -m "release $VERSION"
   # then verify you tagged the right commit
   git log
   ```

1. Reset the `version_info` variable in
   [\_version.py](dockerspawner/_version.py) appropriately with an incremented
   patch version and a `dev` element, then make a commit.

   ```bash
   git add dockerspawner/_version.py
   git commit -m "back to dev"
   ```

1. Push your two commits.

   ```bash
   git push $ORIGIN main --follow-tags
   ```
