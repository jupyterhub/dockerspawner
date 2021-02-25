# How to make a release

`dockerspawner` is a package [available on
PyPI](https://pypi.org/project/dockerspawner/).
The PyPI release is done automatically by TravisCI when a tag
is pushed.

For you to follow along according to these instructions, you need
to have push rights to the [dockerspawner GitHub
repository](https://github.com/jupyterhub/dockerspawner).

## Steps to make a release

1. Checkout master and make sure it is up to date.

   ```bash
   ORIGIN=${ORIGIN:-origin} # set to the canonical remote, e.g. 'upstream' if 'origin' is not the official repo
   git checkout master
   git fetch $ORIGIN master
   git reset --hard $ORIGIN/master
   # WARNING! This next command deletes any untracked files in the repo
   git clean -xfd
   ```

1. Update [CHANGELOG.md](CHANGELOG.md) and add it to
   the working tree.

   ```bash
   git add CHANGELOG.md
   ```

   Tip: Identifying the changes can be made easier with the help of the
   [choldgraf/github-activity](https://github.com/choldgraf/github-activity)
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

1. Reset the `version_info` variable in
   [\_version.py](dockerspawner/_version.py) appropriately with an incremented
   patch version and a `dev` element, then make a commit.

   ```bash
   git add dockerspawner/_version.py
   git commit -m "back to dev"
   ```

1. Push your two commits to master.

   ```bash
   # first push commits without a tags to ensure the
   # commits comes through, because a tag can otherwise
   # be pushed all alone without company of rejected
   # commits, and we want have our tagged release coupled
   # with a specific commit in master
   git push $ORIGIN master
   ```

1. Create a git tag for the pushed release commit and push it.

   ```bash
   git tag -a $VERSION -m "release $VERSION"
   # then verify you tagged the right commit
   git log
   # then push it
   git push $ORIGIN --follow-tags
   ```
