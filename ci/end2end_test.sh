#!/usr/bin/env python
import sys
import subprocess
import os
import tempfile
import shutil
import json

# USAGE
# ./end2end_test.sh <operator-name>

POSSIBLE_OPERATOR_NAMES = [
"aws-lambda", "aws-sagemaker"
]
assert len(sys.argv) == 2, "USAGE: ./end2end_test.sh <operator-name>"
operator_name = sys.argv[1]
assert operator_name in POSSIBLE_OPERATOR_NAMES, f"Invalid <operator_name>. Possible values are {POSSIBLE_OPERATOR_NAMES}"

def check_if_installed(program):
    try:
        subprocess.check_output([program, "--version"])
    except FileNotFoundError:
        raise Exception(f"{program} is not installed!")

check_if_installed("bentoctl")
check_if_installed("terraform")

# set temporary BENTOCTL_HOME
temp_bentoctl_home = tempfile.mkdtemp(prefix="bentoctl-home-dir")
os.environ["BENTOCTL_HOME"] = temp_bentoctl_home
print(os.environ.get("BENTOCTL_HOME"))

print(f"installing {operator_name}")
subprocess.run(f"bentoctl operator install {operator_name}".split())

assert "deployment_config.yaml" in os.listdir(os.curdir), "deployment_config not found!"
subprocess.run("bentoctl generate".split())
TEST_BENTO_NAME = "bentoctl-test-service:latest"
subprocess.run(f"bentoctl build -b {TEST_BENTO_NAME}".split())

# deploy the changes
subprocess.run("bentoctl apply".split())

INTEGRATION_TEST_PATH = os.path.join(os.path.dirname(__file__), "../tests/integration")
terraform_output = subprocess.check_output("terraform output -json".split())
endpoint_url = json.loads(terraform_output)['endpoint']['value']
out = subprocess.run(f"pytest {INTEGRATION_TEST_PATH} --url {endpoint_url}".split())
assert out.returncode == 0, "pytest failed!"

# cleanup
subprocess.run('bentoctl destroy'.split())
