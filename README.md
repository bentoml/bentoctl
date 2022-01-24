<div align="center">
  <h1>bentoctl</h1>
  <i>Best way to deploy BentoML to the cloud.</i>
  <p>
    <img alt="PyPI" src="https://img.shields.io/pypi/v/bentoctl?style=flat-square">
    <img alt="GitHub branch checks state" src="https://img.shields.io/github/checks-status/bentoml/bentoctl/main?style=flat-square">
    <img alt="Codecov" src="https://img.shields.io/codecov/c/github/bentoml/bentoctl?style=flat-square">
</p>
</div>

<br>

bentoctl is a command-line tool that uses easy and approachable YAML syntax to deploy Bento to the cloud.
It supports multiple cloud providers, including AWS, Azure, Google Cloud, and more. It is completely extensible with
operators that can add more cloud providers, uses-cases and workflows.

<div align="center">
<img src="https://raw.githubusercontent.com/bentoml/bentoctl/master/demo.gif"/ alt="demo of bentoctl deploying to AWS-EC2"/>
</div>

## Quick Start

### Installing
You can easily install the python package via pip

> Currently, the bentoctl is in alpha version and you will have to pass the --pre flag to install the pre-release version

```bash
pip install --pre bentoctl
```


To activate tab completion for you shell, source the script in `bentoctl/completion`.
For More info please check [click's documentation](https://click.palletsprojects.com/en/8.0.x/shell-completion/)


### Add AWS EC2 operator

`bentoctl operators add aws-ec2`


### Deploy Bento to EC2

Use the interactive deployment helper. This will generate a deployment YAML file and will then deploy the Bento to the cloud.
```
$ bentoctl deploy
```

`bentoctl deploy` also accepts deployment configuration file.

Save the following configuration file to `deployment_config.yaml`
```yaml
api_version: v1
metadata:
  name: my-bento-deployment
  operator: aws-ec2
spec:
  bento: iris_classifier:latest
  region: us-west-1
  instance_type: t2.micro
  ami_id: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2
  enable_gpus: False
```
Call deploy command
```
$ bentoctl deploy deployment_config.yaml
```

### Delete deployment
```
$ bentoctl delete deployment_config.yaml
```

## Features:

* Supports multiple cloud providers: AWS, Azure, Google Cloud, and more.
* Manages the lifecycle of the BentoML deployment.
* Minimal configuration
* Optimized for CI/CD workflow
* Built with optimization and best practices
* Extensible with operators. Extends or modifies the cloud services and workflow via operators.
