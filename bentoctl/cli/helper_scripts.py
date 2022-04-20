import os
import subprocess

from bentoctl.exceptions import BentoctlException

TERRAFORM_VALUES_FILE = "bentoctl.tfvars"


def terraform_run(cmd: list):
    try:
        subprocess.run(["terraform", *cmd])
    except FileNotFoundError:
        raise BentoctlException(
            "terraform not available. Please make "
            "sure terraform is installed and available your path."
        )


def terraform_destroy():
    if not os.path.exists(os.path.join(os.curdir, TERRAFORM_VALUES_FILE)):
        raise BentoctlException(
            f"{TERRAFORM_VALUES_FILE} not found in current directory."
        )
    terraform_run(["destroy", "-var-file", TERRAFORM_VALUES_FILE])


