# Introduction

bentoctl is a command line tool for deploying BentoML packaged ML models as API endpoint on popular cloud platforms. It automates Bento docker image build, interacts with cloud platform APIs, and allows users easily manage deployments.

Supported platforms:

- [AWS EC2](https://github.com/bentoml/aws-ec2-deploy)
- [AWS Lambda](https://github.com/bentoml/aws-lambda-deploy)
- [AWS SageMaker](https://github.com/bentoml/aws-sagemaker-deploy)
- [Azure Functions](https://github.com/bentoml/azure-functions-deploy)
- [Azure Container Instances](https://github.com/bentoml/azure-container-instances-deploy)
- [Google Cloud Run](https://github.com/bentoml/google-cloud-run-deploy)
- [Google Compute Engine](https://github.com/bentoml/google-compute-engine-deploy)
- [Heroku](https://github.com/bentoml/heroku-deploy)

![demo.gif](https://github.com/bentoml/bentoctl/raw/main/demo.gif)

## Why bentoctl?

- Supports multiple cloud providers: AWS, Azure, Google Cloud, and more.
- Minimal configuration
- Optimized for CI/CD workflow
- Extensible with operators. Extends or modifies the cloud services and workflow via operators.
- Built with optimization and best practices

## How to install

bentoctl can be installed as a python package via pip

```bash
pip install --pre bentoctl
```

> Currently, the bentoctl is in pre-release stage, hence pass the `--pre` to download that version

## What's Next?

- Quickstart Guide will walk you through an example of deploying a bentoml service into AWS Lambda in under 20mins.
- Core Concepts will give a comprehensive tour of the bentoctl components namely operators and deployment config.
- Operator List container all the links to all the available operators and resources to get started.

## Community

- To report a bug or suggest a feature request, use [GitHub Issues](https://github.com/bentoml/bentoctl/issues/new/choose).
- To receive release announcements, please subscribe to our mailing list or join us on [Slack](https://join.slack.com/t/bentoml/shared_invite/enQtNjcyMTY3MjE4NTgzLTU3ZDc1MWM5MzQxMWQxMzJiNTc1MTJmMzYzMTYwMjQ0OGEwNDFmZDkzYWQxNzgxYWNhNjAxZjk4MzI4OGY1Yjg).

## Contributing

There are many ways to contribute to the project:

- If you have any feedback on the project, share it with the community in #bentoctl channel in slack.
- Report issues you're facing and "Thumbs up" on issues and feature requests that are relevant to you.
- Investigate bugs and review other developer's pull requests.
