# AWS Lambda Deployment

AWS Lambda is a serverless solution offered by AWS. Deployment into Lambda is very cheap. You will only be charged on a per request basis. The only drawback is cold-start.

[Github Repo](https://github.com/bentoml/aws-lambda-deploy)
## Instalation
```
> bentoctl operator install aws-lambda
```

## Configuration
* `region`: AWS region for Lambda deployment
* `timeout`: Timeout per request
* `memory_size`: The memory for your function, set a value between 128 MB and 10,240 MB in 1-MB increments
