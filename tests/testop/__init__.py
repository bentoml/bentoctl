from .deploy import deploy
from .update import update
from .describe import describe
from .delete import delete

OPERATOR_NAME = "testop"
<<<<<<< HEAD
CONFIG_SCHEMA = {
=======
OPERATOR_SCHEMA = {
>>>>>>> 2ae59f6 (Added tests for operator functionalities (#1))
    "region": {"required": True, "type": "string", "default": "ap-south-1"},
    "project_id": {"required": True, "type": "string",},
    "max_instances": {
        "required": False,
        "type": "integer",
        "coerce": int,
        "default": 3,
    },
    "min_instances": {
        "required": False,
        "type": "integer",
        "coerce": int,
        "default": 1,
    },
    "instance_type": {
        "required": False,
        "type": "string",
        "coerce": str,
        "default": "m1.tiny",
    },
    "data_capture": {
        "required": False,
        "type": "boolean",
        "coerce": bool,
        "default": False,
    },
}
