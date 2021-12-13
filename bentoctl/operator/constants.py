MAIN_BRANCH = "main"

OFFICIAL_OPERATORS = {
    "heroku": f"bentoml/heroku-deploy:{MAIN_BRANCH}",
    "aws-lambda": f"bentoml/aws-lambda-deploy:{MAIN_BRANCH}",
    "aws-sagemaker": f"bentoml/aws-sagemaker-deploy:{MAIN_BRANCH}",
    "aws-ec2": f"bentoml/aws-ec2-deploy:{MAIN_BRANCH}",
    "azure-functions": f"bentoml/azure-functions-deploy:{MAIN_BRANCH}",
    "azure-container-instances": f"bentoml/azure-container-instances-deploy:{MAIN_BRANCH}",  # noqa: E501
    "google-compute-engine": f"bentoml/google-compute-engine-deploy:{MAIN_BRANCH}",
    "google-cloud-run": f"bentoml/google-cloud-run-deploy:{MAIN_BRANCH}",
}
