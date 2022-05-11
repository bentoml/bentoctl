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

`bentoctl` is a CLI tool for deploying your machine-learning models to any cloud platforms. It built on top of [BentoML: the unified model serving framework](https://github.com/bentoml/BentoML), and makes it easy to bring any BentoML packaged model to production.

👉 [Pop into our Slack community!](https://l.linklyhq.com/l/ktPp) We're happy to help with any issue you face or even just to meet you and hear what you're working on :)

## Features:

* Supports major cloud providers: AWS, Azure, Google Cloud, and more.
* Easy to deploy, update and reproduce model deployments.
* First class integration with Terraform.
* Optimized for CI/CD workflow.
* Extensible with custom operators.
* High performance serving powered by [BentoML](https://github.com/bentoml/BentoML)

## Supported Platforms:

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


## Install bentoctl
```bash
pip install --pre bentoctl
```

| 💡 bentoctl designed to work with BentoML version 1.0.0 and above. For BentoML 0.13 or below, you can use the `pre-v1.0` branch in the operator repositories and follow the instruction in the README. You can also check out the quickstart guide for 0.13 [here](./docs/013-deployment.md).




## Next steps

- [Quickstart Guide](./docs/quickstart.md) walks through a series of steps to deploy a bento to AWS Lambda as API server.
- [Core Concepts](./docs/core-concepts.md) explains the core concepts in bentoctl.
- [Operator List](./docs/operator-list.md) lists official operators and their current status.

## Community

- To report a bug or suggest a feature request, use [GitHub Issues](https://github.com/bentoml/bentoctl/issues/new/choose).
- For other discussions, use [Github Discussions](https://github.com/bentoml/BentoML/discussions) under the [BentoML repo](https://github.com/bentoml/BentoML/)
- To receive release announcements and get support, join us on [Slack](http://join.slack.bentoml.org).


## Contributing

There are many ways to contribute to the project:

- Create and share new operators. Use [deployment operator template](https://github.com/bentoml/bentoctl-operator-template) to get started.
- If you have any feedback on the project, share it with the community in [Github Discussions](https://github.com/bentoml/BentoML/discussions) under the [BentoML repo](https://github.com/bentoml/BentoML/).
- Report issues you're facing and "Thumbs up" on issues and feature requests that are relevant to you.
- Investigate bugs and reviewing other developer's pull requests.
