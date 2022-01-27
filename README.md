<div align="center">
  <h1>bentoctl</h1>
  <i>Fast model deployment with BentoML on cloud platforms</i>
  <p>
    <img alt="PyPI" src="https://img.shields.io/pypi/v/bentoctl?style=flat-square">
    <img alt="GitHub branch checks state" src="https://img.shields.io/github/checks-status/bentoml/bentoctl/main?style=flat-square">
    <img alt="Codecov" src="https://img.shields.io/codecov/c/github/bentoml/bentoctl?style=flat-square">
</p>
</div>

<br>

bentoctl is a CLI tool for deploying your BentoML packaged ML models as API endpoint on popular cloud platforms. It automates Bento docker image build, interactes with cloud platform APIs, and allow users to easily manage their deployment.

## Features:

* Supports major cloud providers: AWS, Azure, Google Cloud, and more.
* Easy to deploy, update and operate cloud deployments.
* Optimized for CI/CD workflow
* Extensible with custom operators.

<div align="center">
<img src="https://raw.githubusercontent.com/bentoml/bentoctl/master/demo.gif"/ alt="demo of bentoctl deploying to AWS-EC2"/>
</div>

## Supported Platforms:

* [AWS EC2](https://github.com/bentoml/aws-ec2-deploy)
* [AWS Lambda](https://github.com/bentoml/aws-lambda-deploy)
* [AWS SageMaker](https://github.com/bentoml/aws-sagemaker-deploy)
* [Azure Functions](https://github.com/bentoml/azure-functions-deploy)
* [Azure Container Instances](https://github.com/bentoml/azure-container-instances-deploy)
* [Google Cloud Run](https://github.com/bentoml/google-cloud-run-deploy)
* [Google Compute Engine](https://github.com/bentoml/google-compute-engine-deploy)
* [Heroku](https://github.com/bentoml/heroku-deploy)


## How to Install
```bash
pip install --pre bentoctl
```

| 💡 bentoctl is in pre-release stage, use the `--pre` to install the pre-release version.


## Get started with bentoctl

1. Create an Bento service. Follow the quick start guide in BentoML or a sample project in the [BentoML Gallery]()
2. Install bentoctl with `pip install --pre bentoctl`
3. Add AWS Lambda operator.
    * Prerequisite:
        * Configured AWS CLI with AWS Cloudformation, Lambda, ECR and API Gateway permissions.
    * Add lambda operator
      ```bash
      bentoctl operator add aws-lambda
      ```
4. Deploy your bento to AWS Lambda with interactive deployment wizard.
    ```bash
    bentoctl deploy --operator aws-lambda
    ```

## Community

- To report a bug or suggest a feature request, use [GitHub Issues](https://github.com/bentoml/bentoctl/issues/new/choose).
- For other discussions, use [Github Discussions](https://github.com/bentoml/BentoML/discussions) under the [BentoML repo](https://github.com/bentoml/BentoML/)
- To receive release announcements and get support, join us on [Slack](https://join.slack.com/t/bentoml/shared_invite/enQtNjcyMTY3MjE4NTgzLTU3ZDc1MWM5MzQxMWQxMzJiNTc1MTJmMzYzMTYwMjQ0OGEwNDFmZDkzYWQxNzgxYWNhNjAxZjk4MzI4OGY1Yjg).


## Contributing

There are many ways to contribute to the project:

- Create and share new operators. Use [deployment operator template](https://github.com/bentoml/bentoctl-operator-template) to get started.
- If you have any feedback on the project, share it with the community in [Github Discussions](https://github.com/bentoml/BentoML/discussions) under the [BentoML repo](https://github.com/bentoml/BentoML/).
- Report issues you're facing and "Thumbs up" on issues and feature requests that are relevant to you.
- Investigate bugs and reviewing other developer's pull requests.
