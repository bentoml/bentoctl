OPERATOR_NAME = "testop"

OPERATOR_DEFAULT_TEMPLATE = "terraform"
OPERATOR_AVAILABLE_TEMPLATES = ["terraform"]

max_instances = 10

OPERATOR_SCHEMA = {
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
    "first_list": {
        "type": "list",
        "schema": {"type": "integer", "help_message": "help message", "coerce": int},
    },
    "instances": {
        "type": "dict",
        "required": True,
        "schema": {
            "min": {
                "type": "integer",
                "coerce": int,
                "default": 1,
                "help_message": "Minimum number of instances",
                "max": max_instances - 1,
                "min": 1,
            },
            "max": {
                "type": "integer",
                "coerce": int,
                "default": 3,
                "help_message": "Maximum number of instances",
                "max": max_instances,
                "min": 2,
            },
        },
    },
    "labels": {
        "type": "list",
        "required": False,
        "schema": {
            "type": "dict",
            "schema": {
                "key": {
                    "type": "string",
                    "required": True,
                    "help_message": "Label key",
                },
                "value": {
                    "type": "string",
                    "required": True,
                    "help_message": "Label value",
                },
            },
        },
    },
}
