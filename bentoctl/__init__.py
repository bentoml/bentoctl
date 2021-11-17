from bentoctl.ops import delete_spec as delete
from bentoctl.ops import deploy_spec as deploy
from bentoctl.ops import describe_spec as describe
from bentoctl.ops import update_spec as update


__all__ = [
    "deploy",
    "update",
    "describe",
    "delete",
]
