# AWS Sagemaker Deployment

[Github Repo](LINK HERE)
Sagemaker is a fully managed service for building ML models. BentoML provides great support for deploying BentoService to AWS Sagemaker without the additional process and work from users. With [BentoML serving framework](https://github.com/bentoml/BentoML) and [bentoctl](https://github.com/bentoml/bentoctl) users can enjoy the performance and scalability of Sagemaker with any popular ML frameworks.

## Instalation
```
> bentoctl operator install aws-sagemaker
```

## Configuration Options

The available spec configuration. 

* `region`: AWS region where Sagemaker endpoint is deploying to
* `instance_type`: The ML compute instance type for Sagemaker endpoint. See https://docs.aws.amazon.com/cli/latest/reference/sagemaker/create-endpoint-config.html for available instance types
* `initial_instance_count`: Number of instances to launch initially.
* `timeout`: timeout for API request in seconds
* `enable_data_capture`: Enable Sagemaker to capture data from requests and responses and store the captured data to AWS S3
* `destination_s3_uri`: S3 bucket path for store captured data
* `initial_sampling_percentage`: The percentage of the data will be captured in S3 bucket.

## Troubleshooting
By default, sagemaker is configured with cloudwatch for metrics and logs. To see the cloudwatch logs for the deployment

1. Open the Amazon Cloudwatch console at https://console.aws.amazon.com/cloudwatch/.
2. In the navigation pane, choose Logs -> Log groups.
3. Head over to /aws/sagemaker/Endpoints/<deployment_name>-endpoint
4. Choose the latest logs stream
