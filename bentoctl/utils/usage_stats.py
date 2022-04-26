import os
import requests

BENTOCTL_DO_NOT_TRACK = "BENTOML_DO_NOT_TRACK"
USAGE_TRACKING_URL = "https://t.bentoml.com"
USAGE_REQUEST_TIMEOUT_SECONDS = 1


def do_not_track() -> bool:
    # Returns True if and only if the environment variable is defined and has value True.
    # The function is cached for better performance.
    return os.environ.get(BENTOCTL_DO_NOT_TRACK, str(False)).lower() == "true"


def get_payload(event_properties: dict) -> dict:
    return {}


def track(event_properties: dict):
    if do_not_track():
        return
    payload = get_payload(event_properties=event_properties)

    requests.post(
        USAGE_TRACKING_URL, json=payload, timeout=USAGE_REQUEST_TIMEOUT_SECONDS
    )
