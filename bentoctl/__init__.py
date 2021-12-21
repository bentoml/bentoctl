from bentoctl.deployment import delete_deployment as delete
from bentoctl.deployment import deploy_deployment as deploy
from bentoctl.deployment import describe_deployment as describe
from bentoctl.deployment import update_deployment as update

__all__ = [
    "deploy",
    "update",
    "describe",
    "delete",
]
