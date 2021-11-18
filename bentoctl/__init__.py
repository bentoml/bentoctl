from bentoctl.operations import delete_spec as delete
from bentoctl.operations import deploy_spec as deploy
from bentoctl.operations import describe_spec as describe
from bentoctl.operations import update_spec as update


__all__ = [
    "deploy",
    "update",
    "describe",
    "delete",
]
