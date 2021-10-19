from datetime import datetime
from pathlib import Path
from collections import namedtuple
import shutil

from . import BCDT_HOME

DEPLOYABLE_TIMESTAMP = "%y%m%d%H%M"


# record for each deployable (deployable_tuple)
d_tuple = namedtuple("deployable", ["operator_name", "deployment_name", "created_at"])


class Store:
    def __init__(self, bcdt_home):
        self.store_home = Path(bcdt_home, "deployments")

    def add(self, operator_name, deployment_name, deployable_path):
        """
        Moves the deployable created after a successful deployment by the operator into
        our local filesystem.
        """
        deployment_path = Path(self.store_home, operator_name, deployment_name)
        deployment_path.mkdir(parents=True, exist_ok=True)
        deployable_name = f"deployable_{datetime.now().strftime(DEPLOYABLE_TIMESTAMP)}"
        dest = deployment_path / deployable_name

        # USE MOVE
        shutil.move(deployable_path, dest)

    def list_deployables(self):
        """
        List all the deployables available.
        """
        deployables_list = []

        # iter through all dirs
        for operator in self._get_dirs(self.store_home):
            for deployment in self._get_dirs(operator):
                for deployable in self._get_dirs(deployment):
                    dt = datetime.strptime(
                        deployable.name.split("_")[1], DEPLOYABLE_TIMESTAMP
                    )
                    deployables_list.append(d_tuple(operator.name, deployment.name, dt))

        return deployables_list

    def list_latest_deployables(self):
        """
        List the latest deployables of every deployment
        """
        latest_deployables = []

        for operator in self._get_dirs(self.store_home):
            for deployment in self._get_dirs(operator):
                latest_deployable = sorted(
                    self._get_dirs(deployment), key=lambda d: d.name
                )[-1]
                dt = datetime.strptime(
                    latest_deployable.name.split("_")[1], DEPLOYABLE_TIMESTAMP
                )
                latest_deployables.append(d_tuple(operator.name, deployment.name, dt))

        return latest_deployables

    def prune_all(self, keep_latest=False):
        """
        prune the store.
        keep_latest: keep the latest deployables of each deployment, del everything else
        """
        for operator in self._get_dirs(self.store_home):
            for deployment in self._get_dirs(operator):
                if keep_latest:
                    ds = self._get_dirs(deployment)
                    ds.remove(sorted(ds, key=lambda ds: ds.name)[-1])
                    for d_path in ds:
                        shutil.rmtree(d_path)
                else:
                    shutil.rmtree(deployment)

    def prune_deployment(self, operator_name, deployment_name):
        """
        Delete all the deployables in deployment_name
        """
        deployment_path = self.store_home / operator_name / deployment_name
        if not deployment_path.exists():
            raise FileNotFoundError(
                f"deployment '{deployment_name}' not found for operator '{operator_name}'"
            )
        shutil.rmtree(self.store_home / operator_name / deployment_name)

    @staticmethod
    def _get_dirs(path: Path):
        return [child for child in path.iterdir() if child.is_dir()]


localstore = Store(BCDT_HOME)
add = localstore.add
list_deployments = localstore.list_latest_deployables
prune = localstore.prune_all
