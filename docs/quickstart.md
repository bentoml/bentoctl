# Quickstart

This guide walks through the steps of building a bento and deploying it to AWS Lambda. It will use the iris classifier bento with `classify` api endpoint created in the BentoML quickstart guide, and then use bentoctl to deploy to AWS lambda.

## Prerequisites

1. Bentoml - BentoML version 1.0 and greater. Please follow the [Installation guide](https://docs.bentoml.org/en/latest/quickstart.html#installation).
2. Terraform - [Terraform](https://www.terraform.io/) is a tool for building, configuring, and managing infrastructure.
3. AWS CLI installed and configured with an AWS account with permission to the Cloudformation, Lamba, API Gateway and ECR. Please follow the [Installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

### Step 1: Create a bento

> Note: Skip to step 2, if you already built a bento with the BentoML 1.0 quick start guide.

Follow the instructions from the [BentoML’s quickstart guide](https://docs.bentoml.org/en/latest/quickstart.html) to build a bento.

### Step 2: Verify bento

To verify the bento, run `bentoml list` to display the available bentos in your local bento store:

```bash
> bentoml list

Tag                               Service    Path                                                          Size       Creation Time
iris_classifier:foereut5zgw3ceb5  bento:svc  /home/user/bentoml/bentos/iris_classifier/foereut5zgw3ceb5  13.97 KiB  2022-01-25 10:25:51
```

### Step 3: Add aws-lambda operator

bentoctl has operators that help deploy bentos to different cloud services.

> **Operator** is a plugin that interacts with the cloud service to perform the bentoctl commands. The operator is responsible for creating and configuring the resources for deploying to the cloud service. Learn more from the [Core Concepts](./core-concepts.md#operators) page.

This guide uses the official aws-lambda operator to deploy and manage deployments. Run the following command to install the operator and its dependencies to your local system

```bash
bentoctl operator add aws-lambda
```

### Step 4: Prepare deployment

A. Create a deployment configuration file
> **Deployment Configuration** is a YAML file that specifies properties of the deployment like which bento service to deploy, what operator to use and other configurations. Learn more from the [Core Concepts](./core-concepts.md#deployment-configuration) page

For this deployment, create a `deployment_config.yaml` file in your current directory with the following content.

```yaml
# deployment_config.yaml
api_version: v1
metadata:
  name: demo
  operator: aws-lambda
  template_type: terraform
spec:
  region: us-west-1
  timeout: 10
  memory_size: 512
```

`bentoctl init` command provides users with an interactive environment to create a deployment configuration file with auto-completion, deployment option descriptions and examples.

B. Generate Terraform project

Use the `bentoctl generate` command to generate a Terraform project.

```bash
bentoctl generate -f deployment.yaml
```

The `-f` flag specifies the deployment configuration file.


### Step 5: Build image for deployment

```bash
bentoctl build -b iris_classifier:foereut5zgw3ceb5 -f deployment.yaml
```


### Step 6: Deploy to Lambda


Initialize Terraform project

```bash
terraform init
```

Apply Terraform changes

```bash
terraform apply -var-file=bentoctl.tfvars --auto-approve
```

### step 7: Make a prediction

The `iris_classifier` uses the `/predict` endpoint for receiving requests so the full URL for the classifier will be in the form `{EndpointUrl}/predict`

```bash
# URL = EndpointUrl + "/predict"
URL=$(bentoctl describe -f deployment_config.yaml | jq -r '.EndpointUrl')/predict
curl -i \
  --header "Content-Type: application/json" \
  --request POST \
  --data '[[5.1, 3.5, 1.4, 0.2]]' \
  $URL
```

### Step 8: Cleanup Deployment

To delete deployment, run the `terraform destroy` command

```bash
terraform destroy -var-file=bentoctl.tfvars --auto-approve
```
