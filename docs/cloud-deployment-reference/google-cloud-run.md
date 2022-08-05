# Google Cloud Run Deployment

Cloud Run is Google Cloud's serverless solution for containers. With Cloud Run, you can develop and deploy highly scalable containerized applications on a fully managed serverless platform. Cloud Run is great for running small to medium models since you only pay for the compute you use and it is super scalable.

[Github Repo](https://github.com/bentoml/google-cloud-run-deploy)

## Instalation

```
> bentoctl operator install google-cloud-run
```

## Configuration Options

This is the list of configurations you can use to deploy your bento to Google Cloud Run. For more information about options check the corresponding Google Cloud Run docs provided.

The required configuration is: 
- `project_id`: Your project id. This will be a unique id for each of your projects, specifying unique resources available to each project. If you haven't created a project, head over to the console and create it
  - check projects you already have by running `gcloud config get-value project`
- `region`: The region to which you want to deploy your Cloud Run service. Check
  the [official list](https://cloud.google.com/run/docs/locations) to know more
  about all the regions available
- `port`: The port that Cloud Run container should listen to. Note: this should be the same as the port that the bento service is listening to (by default 5000)
- `min-instances`: The number of minimum instances that Cloud Run should keep active. Check the [docs](https://cloud.google.com/run/docs/configuring/min-instances)for more info
- `max_instances`: The maximum number of instances Cloud Run should scale up to under load. Check the [dcos](https://cloud.google.com/run/docs/configuring/max-instances) on how to configure it
- `memory`: The RAM that should be available for each instance. If your model uses more than the specified RAM, it will be terminated. Check the [docs](https://cloud.google.com/run/docs/configuring/memory-limits)
- `cpu`: The number of CPUs needed for each instance. Check the [docs](https://cloud.google.com/run/docs/configuring/cpu) for more info
