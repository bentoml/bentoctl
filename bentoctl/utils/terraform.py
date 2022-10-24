import json
import os
import subprocess

from bentoctl.exceptions import BentoctlException

TERRAFORM_VALUES_FILE = "bentoctl.tfvars"
TERRAFORM_INIT_FOLDER = ".terraform"


def terraform_run(cmd: list, return_output: bool = False):
    try:
        if not return_output:
            subprocess.run(["terraform", *cmd], check=False)
        else:
            proc = subprocess.Popen(
                ["terraform", *cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate()
            return proc.returncode, stdout.decode("utf-8"), stderr.decode("utf-8")
    except FileNotFoundError:
        raise BentoctlException(
            "terraform not available. Please make "
            "sure terraform is installed and available your path."
        )


def terraform_destroy(auto_approve):
    if not is_terraform_initialised():
        raise BentoctlException("terraform is not initialised")
    if not os.path.exists(os.path.join(os.curdir, TERRAFORM_VALUES_FILE)):
        raise BentoctlException(
            f"{TERRAFORM_VALUES_FILE} not found in current directory."
        )

    terraform_cmd = [
        "apply",
        "-destroy",
        "-var-file",
        TERRAFORM_VALUES_FILE,
    ]
    if auto_approve:
        terraform_cmd.append("-auto-approve")
    terraform_run(terraform_cmd)


def is_terraform_initialised():
    return os.path.exists(os.path.join(os.curdir, TERRAFORM_INIT_FOLDER))


def terraform_apply(auto_approve):
    if not is_terraform_initialised():
        terraform_run(["init"])

    terraform_cmd = [
        "apply",
        "-var-file",
        TERRAFORM_VALUES_FILE,
    ]
    if auto_approve:
        terraform_cmd.append("-auto-approve")
    terraform_run(terraform_cmd)


def terraform_output():
    return_code, result, error = terraform_run(["output", "-json"], return_output=True)
    if return_code != 0:
        raise BentoctlException(error)
    return json.loads(result)


def is_terraform_applied() -> bool:
    """
    Check if terraform is applied.
    """
    # If the terraform is not currently applied, it will return an empty dict.
    result = terraform_output()
    return True if result else False
