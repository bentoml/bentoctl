# BentoML Cloud Run deployment tool

Cloud Run is GCP's serverless solution for containers. With Cloud Run you can develop and deploy highly scalable containerized applications on a fully managed serverless platform. This is great for running small to medium models since you only pay for the compute you use and its super scalable. With BentoML, you can enjoy the flexibility of Cloud Run with any of the popular framwork.

## Prerequisits

- Google cloud CLI tool

  Install instruction: https://cloud.google.com/sdk/docs/install and make sure all your `gcloud` components are upto data. Run `gcloud components update` to update.

- Docker is installed and running on the machine. Install instruction: https://docs.docker.com/install
- Installed the required python packages. 
  ```bash
  $ pip install -r requirements.txt
  ```

## Quickstart: Deploy Iris Classifier from BentoML into Cloud Run

1. Build and save the Bento Bundle from [BentoML quickstart quide](https://github.com/bentoml/BentoML/blob/master/guides/quick-start/bentoml-quick-start-guide.ipynb)
2. Deploy Iris Classifier into Cloud Run. You can use the `deploy.py` script.
  ```
  $ BENTO_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
  $ python deploy.py $BENTO_BUNDLE_PATH iris-deployment cloud_run_config.json
  
  # Sample output
  Building and Pushing irisclassifier:20210720202108_e3fd4b
  Deploying [irisclassifier:20210720202108_e3fd4b] to Cloud Run Service [iris-deployment]
  Deployment Successful!
  ✔ Service iris-deployment in region asia-south1

  URL:     https://iris-test-vyydquopta-el.a.run.app
  Ingress: all
  Traffic:
    100% LATEST (currently iris-deployment-00003-qiz)

  Last updated on 2021-07-21T06:14:50.139354Z by jamesjithin97@gmail.com:
    Revision iris-deployment-00003-qiz
    Image:         gcr.io/bentoml-3167/irisclassifier:20210720202108_e3fd4b
    Port:          5000
    Memory:        512Mi
    CPU:           1
    Concurrency:   80
    Max Instances: 1
    Timeout:       300s
  ```
  
3. Now the deployment is running. In order to test it out we can make a request with curl to the URL outputed after deployment.
```
$ curl -i \
    --header "Content-Type: application/json" \
    --request POST \
    --data '[[5.1, 3.5, 1.4, 0.2]]' \
    https://iris-test-vyydquopta-el.a.run.app/predict
    
# Sample Output
HTTP/2 200
content-type: application/json
x-request-id: f93cd65b-8ab8-4bf8-9f00-63c1d817576c
x-cloud-trace-context: 904fd4b2145babadfd76783ea478c774;o=1
date: Wed, 21 Jul 2021 07:06:30 GMT
server: Google Frontend
content-length: 3
alt-svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000,h3-T051=":443"; ma=2592000,h3-Q050=":443"; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; ma=2592000,quic=":443"; ma=2592000; v="46,43"

[0]%
```
4. Delete the Cloud Run deployment and clear all the resources used
```
python delete.py iris-deployment
```

## Deployment Operations

### Create new deployment - `deploy.py`
Use command line
```
python deploy.py <BENTO_BUNDLE_PATH> <DEPLOYMENT_NAME> <CONFIG_JSON default is cloud_run_config.json>
```

Using Python API
```python
from deploy import deploy_to_sagemaker

deploy_gcloud_run(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```

### Configuring the deployment
There is an optional config file available that you can use to specifiy the configs for you deployment. These are configurations for the Google Cloud Run so do refer the docs attached for more info about the options. The available options are. 

- `project_id` (required): You project id. This will be a unique id for each of your project and all your resources for that project will come under this. If you haven't created a project, head over to the console and create it. If you have one run `gcloud config get-value project` to get the value
- `port`: The port that Cloud Run container should listen to. Note this should be the same as the port that the bento service is listening too (by default 5000).
- `min-instances`: The number of minimum instances that Cloud Run should keep active. Check the [docs](https://cloud.google.com/run/docs/configuring/min-instances)for more info.
- `max_instances`: The maximum number of instances Cloud Run should scale upto under load. Check the [dcos](https://cloud.google.com/run/docs/configuring/max-instances) on how to configure it.
- `memory`: The RAM that should be available for each instance. If you model uses more that the specified RAM it will be terminated. More info, [docs](https://cloud.google.com/run/docs/configuring/memory-limits)
- `cpu`: The number of CPU spec needed for each instance. Check [docs](https://cloud.google.com/run/docs/configuring/cpu) for more info.
- `allow_unauthenticated` - you can specify if the endpoint should receive request from the public.

## Update existing Deployment - `update.py`
Use Command Line
```
python update.py <BENTO_BUNDLE_PATH> <DEPLOYMENT_NAME> <CONFIG_JSON default is cloud_run_config.json>
```

Use Python API
```
from update import update_gcloud_run

update_gcloud_run(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```

## Describe deployment - `describe.py`
Get the URL and configuration information.

Use Command line
```
python describe.py <DEPLOYMENT_NAME>
```

Use Python API
```
from describe import describe_cloud_run
describe_cloud_run(DEPLOYMENT_NAME, return_json=False)
```

## Delete deployment - `delete.py`
Delete the Cloud Run instances and all the images in the Container Registry.

Use Command line
```
python delete.py <DEPLOYMENT_NAME>
```

Use python API
```
from delete import delete_cloud_run

delete_cloud_run(DEPLOYMENT_NAME)
```
