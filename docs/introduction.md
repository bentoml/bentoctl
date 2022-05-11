# Introduction

bentoctl is a command line tool for deploying BentoML packaged ML models as API endpoint on popular cloud platforms.
It automates Bento docker image build, generate terraform project, and easily manage deployments.

## Why bentoctl?
* Supports major cloud providers: AWS, Azure, Google Cloud, and more.
* Easy to deploy, update and reproduce model deployments.
* First class integration with Terraform.
* Optimized for CI/CD workflow.
* Extensible with custom operators.
* High performance serving powered by [BentoML](https://github.com/bentoml/BentoML)
Supported platforms:

* [AWS Lambda](https://github.com/bentoml/aws-lambda-deploy)
* [AWS SageMaker](https://github.com/bentoml/aws-sagemaker-deploy)
* [AWS EC2](https://github.com/bentoml/aws-ec2-deploy)
* [Google Cloud Run](https://github.com/bentoml/google-cloud-run-deploy)
* [Azure Functions](https://github.com/bentoml/azure-functions-deploy)
* Looking for **Kubernetes**? Try out [Yatai: Model deployment at scale on Kubernetes](https://github.com/bentoml/Yatai).
* **Customize deploy target** by creating bentoctl plugin from the [deployment operator template](https://github.com/bentoml/bentoctl-operator-template).

**Upcoming:**
* [Google Compute Engine](https://github.com/bentoml/google-compute-engine-deploy) (BentoML 1.0 migration in progress)
* [Azure Container Instances](https://github.com/bentoml/azure-container-instances-deploy) (BentoML 1.0 migration in progress)
* [Heroku](https://github.com/bentoml/heroku-deploy) (BentoML 1.0 migration in progress)
* [Knative](https://github.com/bentoml/bentoctl/issues/79) (WIP)


## How to install

Install via pip:

```bash
pip install --pre bentoctl
```

> bentoctl is in pre-release stage, include the `--pre` to download the latest version

## Next steps

- [Quickstart Guide](./quickstart.md) walks through a series of steps to deploy a bento to AWS Lambda as API server.
- [Core Concepts](./core-concepts.md) explains the core concepts in bentoctl.
- [Operator List](./operator-list.md) lists official operators and their current status.

## Community

- To report a bug or suggest a feature request, use [GitHub Issues](https://github.com/bentoml/bentoctl/issues/new/choose).
- To receive release announcements, please subscribe to our mailing list or join us on [Slack](http://join.slack.bentoml.org/).

## Contributing

There are many ways to contribute to the project:

- If you have any feedback on the project, share it with the community in #bentoctl channel in slack.
- Report issues you're facing and "Thumbs up" on issues and feature requests that are relevant to you.
- Investigate bugs and review other developer's pull requests.
