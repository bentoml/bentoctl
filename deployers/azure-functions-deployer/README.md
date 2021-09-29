# BentoML Azure Functions deployment tool

Azure functions is a great option if you want to deploy your model in a serverless manner and forget about autoscalling and want to keep costs to a minimum (per second billing and a free tier of 1 Million requests). Only drawbacks are that first request to your the endpoint will take more time but consecutive requests will be fast. This is due to the cold start issue and you can read the [official docs](https://azure.microsoft.com/en-in/blog/understanding-serverless-cold-start/) to learn more about it and possible fixes. 

## Prerequisites

- An active Azure account configured on the machine with Azure CLI installed and configured
    - Install instruction: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli (Version >= 2.6.0)
    - Configure Azure account instruction: https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli
- Docker is installed and running on the machine.
    - Install instruction: https://docs.docker.com/install
- Install required python packages
    - `$ pip install -r requirements.txt`

## Quickstart
To try this out let us deploy the IrisClassifier demo from the [BentoML quick start guide](https://github.com/bentoml/BentoML/blob/master/guides/quick-start/bentoml-quick-start-guide.ipynb).

1. Build and save Bento Bundle from BentoML quick start guide notebook mentioned above. 

2. Create Azure Container Instance deployment with the deployment tool. Make sure that you copy the [config file](azure_config.json) and make the changes required for your deployment. The reference for the config file is given below.

    Run deploy script in the command line:

    ```bash
    $ BENTO_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
    $ python deploy.py $BENTO_BUNDLE_PATH iristest azure_config.json
    
    # Sample output
    Creating Azure function deployable
    Creating Azure resource group iristest-resource
    Creating Azure storage account iristest0sa
    Creating Azure function plan iristest
    Creating Azure ACR iristest0acr
    Build and push image iristest0acr.azurecr.io/irisclassifier:20210803234622_65f4f4
    Deploying Azure function iristest-fn
    ```



    Get Azure Function deployment information and status

    ```bash
    $ python describe.py iristest

    # Sample output
    ...
        {
      "defaultHostName": "iristest1-fn.azurewebsites.net",
      "enabledHostNames": [
        "iristest1-fn.azurewebsites.net",
        "iristest1-fn.scm.azurewebsites.net"
      ],
      "hostNames": [
        "iristest1-fn.azurewebsites.net"
      ],
      "id": "/subscriptions/6537c276-c5b1-45c2-b3ab-84a22b0cb437/resourceGroups/iristest1-resource/providers/Microsoft.Web/sites/iristest1-fn",
    ...   
    ```

3. Make sample request against deployed service

    ```bash
    $ curl -i \                                                            <<<
      --header "Content-Type: application/json" \
      --request POST \
      --data '[[5.1, 3.5, 1.4, 0.2]]' \
        iristest1-fn.azurewebsites.net/predict
        
    # Sample output
    HTTP/1.1 200 OK
    Content-Length: 3
    Content-Type: application/json
    Server: Kestrel
    Request-Context: appId=cid-v1:a3706f16-a040-4251-a5fa-de9f2abacbea
    x-request-id: d2bebb94-27e3-489e-aa7d-df4ab1c34130
    Date: Wed, 04 Aug 2021 19:22:41 GMT

    [0]%
    ```

4. Delete function deployment

    ```bash
    python delete.py my-first-ec2-deployment
    ```

## Deployment operations

### Create a deployment

Use command line
```bash
$ python deploy.py <Bento_bundle_path> <Deployment_name> <Config_JSON default is azure_config.json>
```

Example:
```bash
$ MY_BUNDLE_PATH=${bentoml get IrisClassifier:latest --print-location -q)
$ python deploy.py $MY_BUNDLE_PATH my_first_deployment azure_config.json
```

Use Python API
```python
from deploy import deploy_to_azure

deploy_to_azure(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```


#### Available configuration options for Azure Function deployments

You can have a config file to specify the specifics for your deployment. There is a sample config provide [here](azure_config.json)
```
{
  "location": "location",
  "min_instances": 1,
  "max_burst": 20,
  "premium_plan_sku": "EP1",
  "function_auth_level": "anonymous",
  "acr_sku": "Standard"
}
```

* `location`: Azure function location for deployment.
* `min_instances`: The number of workers for the app.
* `max_burst`: The maximum number of elastic workers for the app
* `premium_plan_sku`: The SKU of the app service plan. Allowed values: EP1, EP2, EP3. See the link for more info: https://docs.microsoft.com/en-us/azure/azure-functions/functions-premium-plan
* `function_auth_level`: The authentication level for the function. Allowed values: anonymous, function, admin. See link for more info: # https://docs.microsoft.com/en-us/java/api/com.microsoft.azure.functions.annotation.httptrigger.authlevel?view=azure-java-stable
* `acr_sku`: The SKU of the container registry.  Allowed values: Basic, Classic, Premium, Standard. Default is `Standard`


### Update a deployment

Use command line
```bash
$ python update.py <Bento_bundle_path> <Deployment_name> <Config_JSON>
```

Use Python API
```python
from update import update_azure
update_azure(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```

### Get deployment's status and information

Use command line
```bash
$ python describe.py <Deployment_name> <Config_JSON>
```


Use Python API
```python
from describe import describe_azure
describe_azure(DEPLOYMENT_NAME)
```

### Delete deployment

Use command line
```bash
$ python delete.py <Deployment_name> <Config_JSON>
```

Use Python API
```python
from  delete import delete_azure
delete_azure(DEPLOYMENT_NAME)
```
