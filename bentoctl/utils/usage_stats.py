from bentoctl import __version__

# These are internal apis. We will need to make sure update these when BentoML changes.
from bentoml._internal.utils.analytics.usage_stats import (  # noqa pylint: disable=unused-import
    do_not_track,
    track,
    BENTOML_DO_NOT_TRACK,
)


class CliEvent:
    def __init__(
        self,
        cmd_group,
        cmd_name,
        duration_in_ms=None,
        error_type=None,
        return_code=None,
        operator=None,
        version=None,
    ):
        self.cmd_group = cmd_group
        self.cmd_name = cmd_name
        self.duration_in_ms = duration_in_ms
        self.error_type = error_type
        self.return_code = return_code
        self.operator = operator
        self.version = version
        self.bentoctl_version = __version__
        self.event_name = "bentoctl_cli"


def _bentoctl_event(cmd_group, cmd_name, return_value=None):
    if return_value is not None:
        deployment_config = return_value
        version = (
            deployment_config.bento.tag.version if deployment_config.bento else None
        )

        return CliEvent(
            cmd_group,
            cmd_name,
            operator=deployment_config.operator_name,
            version=version,
        )
    else:
        return CliEvent(cmd_group, cmd_name)


cli_events_map = {"bentoctl": _bentoctl_event}
