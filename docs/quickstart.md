# Quickstart

This guide walks through the steps of building a bento and deploying it to AWS Lambda. It will use the iris classifier bento with `classify` api endpoint created in the BentoML quickstart guide, and then use bentoctl to deploy to AWS lambda.

## Prerequisites

1. Bentoml - BentoML version 1.0 and greater. Please follow the [Installation guide](https://docs.bentoml.org/en/latest/quickstart.html#installation).
2. Terraform - [Terraform](https://www.terraform.io/) is a tool for building, configuring, and managing infrastructure.
3. AWS CLI installed and configured with an AWS account with permission to the Cloudformation, Lamba, API Gateway and ECR. Please follow the [Installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

### Step 1: Import a bento

> Note: Skip to step 2, if you already built a bento with the [BentoML’s quickstart guide](https://docs.bentoml.org/en/latest/quickstart.html).

Import the iris-classifier bento from s3 to your local machine by running
```bash
bentoml import s3://bentoml.com/quickstart/iris_classifier.bento
```
The code for this bento can be found in [bentoml/gallery/quickstart](https://github.com/bentoml/gallery/tree/main/quickstart). This bento has a `/classify` endpoint that exposes an sklearn model trained on the iris dataset.

### Step 2: Verify bento

To verify the bento, run `bentoml get` to display the properties of the bento from your local bento store:

```bash
bentoml get iris_classifier:latest
```

### Step 3: Install aws-lambda operator

bentoctl has operators that help deploy bentos to different cloud services.

> **Operator** is a plugin that interacts with the cloud service to perform the bentoctl commands. The operator is responsible for creating and configuring the resources for deploying to the cloud service. Learn more from the [Core Concepts](./core-concepts.md#operators) page.

This guide uses the official aws-lambda operator to deploy and manage deployments. Run the following command to install the operator and its dependencies to your local system

```bash
bentoctl operator install aws-lambda
```

### Step 4: Generate deployment files

bentoctl uses the deployment configuration to specify the deployment properties and generate Terraform project from that.

> **Deployment Configuration** is a YAML file that specifies properties of the deployment like which bento service to deploy, what operator to use and other configurations. Learn more from the [Core Concepts](./core-concepts.md#deployment-configuration) page


bentoctl offers an interactive cli command, `bentoctl init`, to guide users to generate the deployment configuration and the terraform projects.

```bash
bentoctl init

Bentoctl Interactive Deployment Config Builder

Welcome! You are now in interactive mode.

This mode will help you setup the deployment_config.yaml file required for
deployment. Fill out the appropriate values for the fields.

(deployment config will be saved to: ./deployment_config.yaml)

api_version: v1
name: quickstart
operator: aws-lambda
template: terraform
spec:
    region: us-west-1
    timeout: 10
    memory_size: 512
filename for deployment_config [deployment_config.yaml]:
deployment config generated to: deployment_config.yaml
✨ generated template files.
  - bentoctl.tfvars
  - main.tf
```

### Step 5: Build image for deployment

Bentoctl prepares the docker image base on the cloud service's requirements, and then build and push the docker image to the deployment registry.

```bash
bentoctl build -b iris_classifier:btzv5wfv665trhcu -f deployment_config.yaml

Step 1/20 : FROM bentoml/bento-server:1.0.0a7-python3.7-debian-runtime
 ---> dde7b88477b1
Step 2/20 : ARG UID=1034
 ---> Running in b8f4ae1d8b08
 ---> e6c313c8d9ea
Step 3/20 : ARG GID=1034
....
Step 20/20 : ENTRYPOINT [ "/opt/conda/bin/python", "-m", "awslambdaric" ]
 ---> Running in 4e56057f3b18
 ---> dca82bca9034
Successfully built dca82bca9034
Successfully tagged aws-lambda-iris_classifier:btzv5wfv665trhcu
🔨 Image build!
The push refers to repository [192023623294.dkr.ecr.us-west-1.amazonaws.com/quickstart]
btzv5wfv665trhcu: digest: sha256:ffcd120f7629122cf5cd95664e4fd28e9a50e799be7bb23f0b5b03f14ca5c672 size: 3253
32096534b881: Pushed
f709d8f0f57d: Pushed
7d30486f5c78: Pushed
...
c1065d45b872: Pushed
🚀 Image pushed!
✨ generated template files.
  - bentoctl.tfvars
The push refers to repository [192023623294.dkr.ecr.us-west-1.amazonaws.com/quickstart]
```

Afterward, bentoctl will update the terraform variables with the docker image information


### Step 6: Deploy to Lambda


Initialize Terraform project

```bash
terraform init
```

Apply Terraform changes

```bash
terraform apply -var-file=bentoctl.tfvars --auto-approve

aws_iam_role.lambda_exec: Creating...
aws_apigatewayv2_api.lambda: Creating...
aws_apigatewayv2_api.lambda: Creation complete after 1s [id=ka8h2p2yfh]
aws_cloudwatch_log_group.api_gw: Creating...
aws_cloudwatch_log_group.api_gw: Creation complete after 0s [id=/aws/api_gw/quickstart-gw]
aws_apigatewayv2_stage.lambda: Creating...
aws_iam_role.lambda_exec: Creation complete after 3s [id=quickstart-iam]
aws_iam_role_policy_attachment.lambda_policy: Creating...
aws_lambda_function.fn: Creating...
aws_apigatewayv2_stage.lambda: Creation complete after 2s [id=$default]
aws_iam_role_policy_attachment.lambda_policy: Creation complete after 1s [id=quickstart-iam-20220414203448384500000001]
aws_lambda_function.fn: Still creating... [10s elapsed]
aws_lambda_function.fn: Still creating... [20s elapsed]
aws_lambda_function.fn: Still creating... [30s elapsed]
aws_lambda_function.fn: Still creating... [40s elapsed]
aws_lambda_function.fn: Creation complete after 41s [id=quickstart-function]
aws_lambda_permission.api_gw: Creating...
aws_cloudwatch_log_group.lg: Creating...
aws_apigatewayv2_integration.lambda: Creating...
aws_lambda_permission.api_gw: Creation complete after 0s [id=AllowExecutionFromAPIGateway]
aws_cloudwatch_log_group.lg: Creation complete after 0s [id=/aws/lambda/quickstart-function]
aws_apigatewayv2_integration.lambda: Creation complete after 1s [id=8gumjws]
aws_apigatewayv2_route.root: Creating...
aws_apigatewayv2_route.services: Creating...
aws_apigatewayv2_route.root: Creation complete after 0s [id=jjp5f23]
aws_apigatewayv2_route.services: Creation complete after 0s [id=8n57a1d]

Apply complete! Resources: 11 added, 0 changed, 0 destroyed.

Outputs:

base_url = "https://ka8h2p2yfh.execute-api.us-west-1.amazonaws.com/"
function_name = "quickstart-function"
image_tag = "192023623294.dkr.ecr.us-west-1.amazonaws.com/quickstart:btzv5wfv665trhcu"
```

### step 7: Make a prediction

The `iris_classifier` uses the `/classify` endpoint for receiving requests so the full URL for the classifier will be in the form `{EndpointUrl}/classify`

```bash
URL=$(terraform output -json | jq -r .base_url.value)classify
curl -i \
  --header "Content-Type: application/json" \
  --request POST \
  --data '[5.1, 3.5, 1.4, 0.2]' \
  $URL

HTTP/2 200
date: Thu, 14 Apr 2022 23:02:45 GMT
content-type: application/json
content-length: 1
apigw-requestid: Ql8zbicdSK4EM5g=

0%
```

### Step 8: Cleanup Deployment

To delete deployment, run the `terraform destroy` command

```bash
terraform destroy -var-file=bentoctl.tfvars --auto-approve
```
