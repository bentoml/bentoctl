# Operator

Operator is a standardized way to create and manage deployments. It describes how to 
create a deployment, how to update it, and how to delete it. It also includes schema and validation
for the configurations.

Checkout operator template repo for example: https://github.com/bentoml/deployment-operator-template



# Operator Registry

Bentoctl manage installed operators with operator registry. The default location is `{bentoctl_home}/operators/{operator_name}`

Registry will read `operator_list.json` file in the directory to get the list of installed operators.

Example `operator_list.json`:
```
{
    "aws-lambda": {
        "path": "/Users/bozhaoyu/bentoctl/operators/aws-lambda",
        "git_url": "https://github.com/bentoml/aws-lambda-deploy.git",
        "git_branch": "main",
        "is_local": false,
        "version": "0.1.0"
    }
}
```


Operator registry can add/update/list/remove operators.

Registry add can add operator from the official operator list, local path or from remote git repository.

Registry update will update the operator based on their add location.

