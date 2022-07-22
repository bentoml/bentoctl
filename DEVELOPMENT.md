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


### End2End Testing

bentoctl depends on a lot of external dependencies like Terraform, different
Terraform Providers, Cloud Service Providers and its APIs. This makes End2End
testing very usefull.

There is a bentoml service in ./tests/testbento that can be used as the bento
you deploy into the cloud providers. 

1. Build this bento locally. `bentoml build ./tests/testbento`
2. Serve the bento locally if you want. `bentoml serve
   bentoctl-test-service:latest`
3. Run the end2end test with pytest. `pytest tests/integration --url
   http://localhost:3000`
   The `--url` flag is used to pass the URL of the endpoint where the bento
   service is available.

Now lets deploy this `bentoctl-test-service` into the cloud with the operator to
test. In this example, lets use `aws-lambda`.

1. Install operator `bentoctl operator install aws-lambda`. Make sure to
   configure the AWS CLI (or others based on the cloud that you are deploying
   into)
2. Run `bentoctl init` and configure the deployment.
3. Run `bentoctl build -b bentoctl-test-service:latest` and `bentoctl apply` to
   deploy to the cloud service
4. After the deployment is done. Note down the `endpoint` URL and run `pytest
   tests/integration --url <endpoint url>`. This will run the test on the
   endpoint and different paths.

Perform these steps for each of the opeators you want to test.
