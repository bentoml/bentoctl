# Google Compute Engine Deployment

Google Compute Engine offers you a secure and customizable compute service that lets you create and run virtual machines on Google's infrastructure. You can choose from a wide range of CPU, GPU, and memory configurations to meet the needs of your models.

[Github Repo](https://github.com/bentoml/google-compute-engine-deploy)

## Instalation
```
> bentoctl operator install google-compute-instance
```

## Configuration Options
* `project_id`: The project ID for the GCP project you want to deploy to. Make sure the VM instances API is activated. 
* `zone`: The zone to which you want to deploy. To get the complete list of available zones run `gcloud compute zones list`
* `machine_type`: This specifies the machine type you want to use. You can use different machine types based on the resource requirements of your model. To get a list of all the machine types available run `gcloud compute machine-types list`
