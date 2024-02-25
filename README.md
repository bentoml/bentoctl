## ⚠️ BentoCTL project has been deprecated

Plese see the latest BentoML documentation on OCI-container based deployment workflow: https://docs.bentoml.com/

## 🚀 Fast model deployment on any cloud



[![join_slack](https://badgen.net/badge/Join/Community%20Slack/cyan?icon=slack&style=flat-square)](https://join.slack.bentoml.org)

bentoctl helps deploy any machine learning models as production-ready API endpoints on the cloud, supporting AWS SageMaker, AWS Lambda, EC2, Google Compute Engine, Azure, Heroku and more.

👉 [Join our Slack community today!](https://l.bentoml.com/join-slack)

✨ Looking deploy your ML service quickly? You can checkout [BentoML Cloud](https://www.bentoml.com/bentoml-cloud/)
for the easiest and fastest way to deploy your bento. It's a full featured, serverless environment with a model repository and built in monitoring and logging.


## Highlights

* Framework-agnostic model deployment for Tensorflow, PyTorch, XGBoost, Scikit-Learn, ONNX, and many more via
 [BentoML: the unified model serving framework](https://github.com/bentoml/bentoml).
* Simplify the deployment lifecycle of deploy, update, delete, and rollback.
* Take full advantage of BentoML's performance optimizations and cloud platform features out-of-the-box.
* Tailor bentoctl to your DevOps needs by customizing deployment operator and Terraform templates.


## Getting Started

- [💻 Quickstart Guide](./docs/quickstart.md) - Deploy your first model to AWS Lambda as a serverless API endpoint.
- [📖 Core Concepts](./docs/core-concepts.md) - Learn the core concepts in bentoctl.
- [🕹️ Operators List](./docs/operator-list.md) - List of official operators and advanced configuration options.
- [💬 Join Community Slack](https://l.linklyhq.com/l/ktPp) - Get help from our community and maintainers.


## Supported Platforms:

* [AWS Lambda](https://github.com/bentoml/aws-lambda-deploy)
* [AWS SageMaker](https://github.com/bentoml/aws-sagemaker-deploy)
* [AWS EC2](https://github.com/bentoml/aws-ec2-deploy)
* [Google Cloud Run](https://github.com/bentoml/google-cloud-run-deploy)
* [Google Compute Engine](https://github.com/bentoml/google-compute-engine-deploy)
* [Azure Container Instances](https://github.com/bentoml/azure-container-instances-deploy)
* [Heroku](https://github.com/bentoml/heroku-deploy)


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


## Licence

[Elastic License 2.0 (ELv2)](https://github.com/bentoml/bentoctl/blob/main/LICENSE.md)
