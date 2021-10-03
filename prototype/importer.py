import importlib
import sys
import os
import subprocess
import json


def run_shell_command(command, cwd=None, env=None, shell_mode=False):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell_mode,
        cwd=cwd,
        env=env,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode == 0:
        try:
            return json.loads(stdout.decode("utf-8")), stderr.decode("utf-8")
        except json.JSONDecodeError:
            return stdout.decode("utf-8"), stderr.decode("utf-8")
    else:
        raise Exception(
            f'Failed to run command {" ".join(command)}: {stderr.decode("utf-8")}'
        )


def import_module(name, path):
    import importlib.util
    from importlib.abc import Loader

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert isinstance(spec.loader, Loader)
    spec.loader.exec_module(module)
    return module


def make_deployment():
    """Makes the deployment with the specified deployer"""
    deployer_path = "../deployers/aws-lambda-deployer"
    sys.path.append(deployer_path)
    deployer = import_module(
        "aws_lambda_deployer", os.path.join(deployer_path, "deployer_conf.py")
    )
    sys.path.remove(deployer_path)

    deployer.deploy(
        "../../sklearn/saved_dir", "iris-test", "../../sklearn/lambda_config.json"
    )


def delete_deployment():
    """
    delete the deployment
    """
    deployer_path = "../deployers/aws-lambda-deployer"
    sys.path.append(deployer_path)
    deployer = import_module(
        "aws_lambda_deployer", os.path.join(deployer_path, "deployer_conf.py")
    )
    sys.path.remove(deployer_path)

    deployer.delete("iris-test", "../../sklearn/lambda_config.json")


def install_deps():
    """
    Install all dependencies
    """
    deployer_path = "../deployers/aws-lambda-deployer"
    print("installing deps...")
    outs = run_shell_command(
        ["pip", "install", "-r", os.path.join(deployer_path, "requirements.txt")]
    )
    print(outs)


def list_deployers():
    """
    List all the deployers available in the path ~/btcd/deployers or BTDC_DEPLOYER_PATH
    """
    BTDC_DEPLOYER_PATH = "../deployers"
    deployers = []
    for d in os.listdir(BTDC_DEPLOYER_PATH):
        if os.path.exists(os.path.join(BTDC_DEPLOYER_PATH, d, "deployer_conf.py")):
            deployers.append(d)

    return deployers
