from bentoctl.deployment import delete_deployment as delete
from bentoctl.deployment import deploy_deployment as deploy
from bentoctl.deployment import describe_deployment as describe
from bentoctl.deployment import update_deployment as update

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

# Find bentoctl version managed by pyproject.toml
__version__: str = importlib_metadata.version("bentoctl")

__all__ = [
    "deploy",
    "update",
    "describe",
    "delete",
]
