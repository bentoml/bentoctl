import os
import shutil


def deploy(bento_path, deployment_name, deployment_spec):
    print("deploying with: ", bento_path, deployment_name, deployment_spec)
    deployabe_path = os.path.abspath("./testop_deployable")
    cur_path = os.path.dirname(__file__)
    deployable_file = os.path.join(cur_path, "./testdeployable")
    shutil.copytree(deployable_file, deployabe_path)

    return deployabe_path
