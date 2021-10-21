from deploy import deploy
from update import update
from describe import describe
from delete import delete

OPERATOR_NAME = "testop"
REQUIRED_FIELDS = ["region"]
DEFAULT_FIELDS = {
    "max_instances": 3,
    "min_instances": 1,
    "instance_type": "m1.tiny",
    "data_capture": False,
}
