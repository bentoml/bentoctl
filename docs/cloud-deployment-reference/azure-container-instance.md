# Azure Container Instance Deployment
Azure Container Instances is a great deployment strategy for deploying ML model endpoints that you know will get consistent traffic or want to take advantage of accelerators like GPUs. You can also add autoscaling capabilities.

[Github Repo](https://github.com/bentoml/azure-container-instances-deploy)

## Installation
```
> bentoctl operator install azure-container-instances
```

## Configuration Options

* `resrouce_group`: Resource group into which the resources have to be created.
* `acr_name`: The name of Azure Container Registry to use to store images.
* `memory`: The memory (in GBs) you want each instance to have.
* `cpu_count`: The number of CPU cores you want for your instance.
* `bentoml_port`: The port you want the endpoint to use. By default it is 5000

