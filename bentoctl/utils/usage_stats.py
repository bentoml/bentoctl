import os
import typing as t
from functools import lru_cache

import attr

# These are internal apis. We will need to make sure update these when BentoML changes
from bentoml._internal.utils.analytics.schemas import EventMeta
from bentoml._internal.utils.analytics.usage_stats import (  # noqa pylint: disable=unused-import
    BENTOML_DO_NOT_TRACK,
    track,
)

from bentoctl import __version__
from bentoctl.deployment_config import DeploymentConfig


@lru_cache(maxsize=1)
def do_not_track() -> bool:  # pragma: no cover
    """
    Returns True if and only if the environment variable is defined and has value True.
    The function is cached for better performance.
    """
    return os.environ.get(BENTOML_DO_NOT_TRACK, str(False)).lower() == "true"


@attr.define
class BentoctlCliEvent(EventMeta):
    cmd_group: str
    cmd_name: str
    duration_in_ms: t.Optional[t.Any] = attr.field(default=None)
    error_type: t.Optional[str] = attr.field(default=None)
    return_code: t.Optional[int] = attr.field(default=None)
    operator: t.Optional[str] = attr.field(default=None)
    version: t.Optional[str] = attr.field(default=None)
    bentoctl_version: str = __version__


def _bentoctl_event(
    cmd_group: str, cmd_name: str, return_value: t.Optional[DeploymentConfig] = None
):
    if return_value is not None:
        deployment_config = return_value
        version = (
            deployment_config.bento.tag.version if deployment_config.bento else None
        )

        return BentoctlCliEvent(
            cmd_group,
            cmd_name,
            operator=deployment_config.operator_name,
            version=version,
        )
    else:
        return BentoctlCliEvent(cmd_group, cmd_name)


cli_events_map = {"bentoctl": _bentoctl_event}
