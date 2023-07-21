# Quickstart

This guide walks through the steps of building a bento and deploying it. For completion, we will be deploying into AWS Lambda. You can also try deploying to other cloud services. The entire list of cloud services and configuration is mentioned in the [cloud deployment reference](./cloud-deployment-reference/) section.

This quickstart will use the iris classifier bento with `/classify` API endpoint created in the BentoML quickstart guide as an example bento.

## Prerequisites

1. Bentoml - BentoML version 1.0 and greater. Please follow the [Installation guide](https://docs.bentoml.com/en/latest/installation.html).
2. Terraform - [Terraform](https://www.terraform.io/) is a tool for building, configuring, and managing infrastructure.
3. AWS CLI installed and configured with an AWS account with permission to the Cloudformation, Lamba, API Gateway and ECR. Please follow the [Installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

### Step 1: Import a bento

> Note: Skip to step 2, if you already built a bento with the [BentoML’s quickstart guide](https://docs.bentoml.org/en/latest/quickstart.html).

Import the iris-classifier bento from s3 to your local machine by running
```bash
> pip install fs-s3fs
> bentoml import s3://bentoml.com/quickstart/iris_classifier.bento
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

This guide uses the official aws-lambda operator to deploy and manage deployments. Check the [aws-lambda operator docs](./cloud-deployment-reference/aws-lambda.md) for more info about the operator. 

> Note: If you want to deploy to any other service check out the available operators [here](./cloud-deployment-reference) and follow along. Sections that need attention when using a different operator will be mentioned. Refer to the specific operator documentation in that case.

Run the following command to install the operator and its dependencies to your local system

```bash
bentoctl operator install aws-lambda
```

### Step 4: Generate deployment files

bentoctl uses the deployment configuration to specify the deployment properties and bentoctl generates the terraform files from that.

> **Deployment Configuration** is a YAML file that specifies properties of the deployment like which bento service to deploy, what operator to use, and other cloud service-specific configurations. Learn more from the [Core Concepts](./core-concepts.md#deployment-configuration) page

bentoctl offers an interactive CLI command, `bentoctl init`, to guide users to generate the deployment configuration and the terraform files.

```bash
bentoctl init

Bentoctl Interactive Deployment Config Builder

Welcome! You are now in interactive mode.

This mode will help you setup the deployment_config.yaml file required for
deployment. Fill out the appropriate values for the fields.

(deployment config will be saved to: ./deployment_config.yaml)

api_version: v1
name: quickstart
operator:
    name: aws-lambda
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

Bentoctl prepares the docker image base on the cloud service's requirements, and then builds and pushes the docker image to the deployment registry. The registry is created for you by the operator.

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

> Note: The build command generates the required terraform files that define the image to use and resources to create. Do commit these files in order to version control your infrastructure. More info [here](https://www.hashicorp.com/blog/version-controlled-infrastructure-with-github-and-terraform)

### Step 6: Deploy to Lambda

Now you have configured the deployment and built the bento and pushed it into the registry. Now you can run `bentoctl apply` command to deploy the bento as an endpoint in the cloud. 

The `apply` under the hood runs the terraform commands for you. Before applying
the changes Terraform will list the changes it is planning to make and ask for
permission to create this. This is a good chance to verify the resource that is
being created for you and if everything looks good approve it. For most custom
deployment strategies refer to [Customize deployments with Terraform
guide](./customizing-deployments.md). 

```bash
bentoctl apply -f deployment_config.yaml

data.aws_ecr_repository.service: Reading...
data.aws_ecr_repository.service: Read complete after 2s [id=testlambda]
data.aws_ecr_image.service_image: Reading...
data.aws_ecr_image.service_image: Read complete after 1s [id=sha256:b0637046b983acc0f52d4b387ddabcf8bec9d61b214b169cf36cd299854701c5]

Terraform used the selected providers to generate the following execution plan. Resource
actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_apigatewayv2_api.lambda will be created
  + resource "aws_apigatewayv2_api" "lambda" {
      + api_endpoint                 = (known after apply)
      + api_key_selection_expression = "$request.header.x-api-key"
      + arn                          = (known after apply)

... other output from terraform

aws_apigatewayv2_integration.lambda: Creation complete after 2s [id=jeaalbk]
aws_apigatewayv2_route.services: Creating...
aws_apigatewayv2_route.root: Creating...
aws_cloudwatch_log_group.lg: Creation complete after 4s [id=/aws/lambda/testlambda-function]
aws_apigatewayv2_route.root: Creation complete after 3s [id=z8i4az1]
aws_apigatewayv2_route.services: Creation complete after 3s [id=zpxehl0]

Apply complete! Resources: 11 added, 0 changed, 0 destroyed.

Outputs:

endpoint = "https://ti7d9u5jkl.execute-api.us-west-1.amazonaws.com/"
function_name = "testlambda-function"
image_tag = "213386773652.dkr.ecr.us-west-1.amazonaws.com/testlambda:of7al2xz6g2vh74c"

```

### step 7: Make a prediction

The `iris_classifier` uses the `/classify` endpoint for receiving requests so the full URL for the classifier will be in the form `{endpoint}/classify`

```bash
URL=$(terraform output -json | jq -r .endpoint.value)/classify
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
### Optional Step: Update Deployment

The section is optional but we will walk through the update steps for
bentoctl. If you have some experience with [bentoml's
quickstart](https://docs.bentoml.org/en/latest/tutorial.html) feel free to try
it. 

Make a small modification to the bentoml service file and build the bentoml
service again. Note down the tag that is generated. Now let's deploy the new
bento.

First, we have to run the build step again. This will create the new docker image to deploy and push it into the registry. It will also modify the terraform files so that they point to the new image instead of the old one.
```bash
> bentoctl build -b <new-bento-tag> -f deployment_config.yaml
```

With the new bento uploaded, we can run `bentoctl apply` to deploy the latest changes. This will run terraform and make the necessary changes in order to point to the latest deployment. 
```bash
> bentoctl apply -f deployment_config.yaml
```

### Step 8: Cleanup Deployment

To delete deployment, run the `bentoctl destroy` command. bentoctl will run `terraform destroy` command that will shut down and remove all the services created. Running `bentoctl destroy` will also delete the docker repository created and all the images in it.

```bash
bentoctl destroy -f deployment_config.yaml
```

Congrats! hopefully, you have successfully deployed your bento in the cloud. To
learn more, feel free to check out: 
- the [Core Concepts](./core-concepts.md) page to know more about the internals
  of bentoctl. 
- the [aws-lambda reference](./cloud-deployment-reference/aws-lambda.md) to know
  more about deploying to AWS Lambda or 
- other cloud services that are supported are documented in [Cloud Service
  Guild](./cloud-deployment-reference)
