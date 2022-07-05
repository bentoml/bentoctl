## What is in this dir?

./testbento - a bento for integration testing.
./test-operator - an operator that implements the basic parts. Used for easier unit
testing.
./unit/ - contains all the unit tests.
./integration - contains all integration tests

## Integration Test

Integration test can be run via pytest. It takes two extra arguments.
1. `--url` - the url for the bentoml server created in the cloud.
2. `--target` - where the bentoml service is hosted. Tests are modified based on
   the cloud-service in which bentoml is running. Values currently supported:
    - default
    - sagemaker

Eg.
```
# testing locally
> pytest tests/integration --url <local_endpoint>

# testing sagemaker
> pytest tests/integration --url <sagemaker-endpoint> --sagemaker
```
