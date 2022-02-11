## Install bentoctl from source

Make sure you have [Git](https://git-scm.com/), [Python3.7+](https://www.python.org/downloads/) and [poetry](https://python-poetry.org/docs/#installation) installed on your system.
Poetry is used for dependency management and packaging.

Clone the source code from bentoctl's repository:
```base
git clone https://github.com/bentoml/bentoctl.git && cd bentoctl
```

It is recommended that you install bentoctl into a virtual environment like for developing [virtualenv](https://virtualenv.pypa.io/en/latest/) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).
Activate your virtural environment and install the bentoctl and its dependencies using poetry.
```base
poetry install
```
This will make `bentoctl` available on your system which links to the sources of your local clone
and will pick up changes you made locally.
Test out the bentoctl installation either with bash or python
```bash
bentoctl --version
```

```python
print(bentoctl.__version__)
```

### Install bentoctl from other forks or branches

`pip` also supports installing directly from remote git repository. This makes it
easy to try out new bentoctl feature that has not been released, test changes in a pull
request. For example, to install bentoctl from its main branch:

```bash
pip install git+https://github.com/bentoml/bentoctl.git
```

Or to install from your own fork of bentoctl:
```bash
pip install git+https://github.com/{your_github_username}/bentoctl.git
```

You can also specify what branch to install from:
```bash
pip install git+https://github.com/{your_github_username}/bentoctl.git@{branch_name}
```


### How to release to pypi

Run `release.sh` in the dev directory

```bash
#from root directory
./dev/release.sh VERSION REPO
```
`version` is the version number of the release. It needs to be semver compliant.
`repo` only accept testpypi and pypi as valid values.

For testpypi release:
It will update the package version and publish to testpypi registry.

For pypi release:
It will create a new commit on the main branch and a new tag. Both will push to the remote.
And then publish to pypi registry.
