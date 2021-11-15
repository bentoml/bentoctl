OPERATOR_NAME = "testop"

OPERATOR_SCHEMA = {
    "region": {"required": True, "type": "string", "default": "ap-south-1"},
    "project_id": {"required": True, "type": "string",},
    "region": {
        "required": True,
        "type": "string",
        "default": "ap-south-1",
        "help_message": "The AWS region to which you want to deploy the service to.",
    },
    "project_id": {
        "required": True,
        "type": "string",
        "help_message": "project_id of the project that holds this deployment",
    },
    "max_instances": {
        "required": False,
        "type": "integer",
        "coerce": int,
        "default": 3,
        "help_message": "maximum number of instances the deployment should scale up to",
    },
    "min_instances": {
        "required": False,
        "type": "integer",
        "coerce": int,
        "default": 1,
        "help_message": "Minimum number of instances the deployment should scale "
        "down to.",
    },
    "instance_type": {
        "required": False,
        "type": "string",
        "coerce": str,
        "default": "m1.tiny",
        "help_message": "The EC2 instance type for each instance. Check "
        "https://aws.amazon.com/ec2/instance-types to see all available instances",
    },
    "data_capture": {
        "required": False,
        "type": "boolean",
        "coerce": bool,
        "default": False,
        "help_message": "Should all the data related to the model invocation be"
        " captured and saved.",
    },
}
