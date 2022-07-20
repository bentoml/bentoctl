## Welcome to the bentoctl docs

### Introduction
bentoctl is a command-line tool for deploying BentoML packaged ML models as API
endpoints on popular cloud platforms. It helps facilitate the handoff of an ML
model from data scientists to DevOps engineers by providing an easy way to
integrate the service with existing deployment pipelines.

bentoctl simplifies
- building the bento for the cloud platform of choice
- creating the registry and pushing the bento into it
- generating the terraform project with the all required components
- facilitating gitops workflow for deploying models thanks to the tight
  integration with bentoml

Bentoctl uses [terraform](https://www.terraform.io/) under the hood to create
and manage the cloud infrastructure. Terraform is an infrastructure as code
(IaC) tool that allows you to build, change, and version infrastructure safely
and efficiently. Bentoctl generates the required terraform files that are
optimized for your models with minimal configuration from your end. While the
generated terraform files are a great starting point with sensible defaults, you
can configure them to meet your specific needs also.

This means bentoctl provides ease of use and flexibility to get your models
built with bentoml to any cloud service you want.

### Where to go from here
1. [Quickstart](./quickstart.md) - See bentoctl in action. This guide walks you
   through the different steps required for deploying the model into the cloud.
   Will be using deploying to AWS Lambda as an example.
2. [Core Concepts](./core-concepts.md) - Introduces the philosophy behind
   bentoctl and the different components.
3. [Customising Deployments](./customizing-deployments.md) - Explain the different
   terraform files generated and how to modify them to meet specific deployment
   setups.
4. [Managing Deployments](./managing-deployments.md) - Explain what terraform
   cloud is and how it can help with managing different deployments in a team.
   We will also go through an example.
5. [Cloud Deployment Reference](./cloud-deployment-reference) - Lists all the supported
   deployment targets and has the references and best practices for these
   specific targets.
