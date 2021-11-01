import typing as t

from bcdt.ops import delete_spec as delete
from bcdt.ops import deploy_spec
from bcdt.ops import describe_spec as describe
from bcdt.ops import update_spec as update


# TODO
def deploy(name: str, operator: str, bento: str, spec: str):
    pass


__all__ = [
    "deploy",
    "update",
    "describe",
    "delete",
]
