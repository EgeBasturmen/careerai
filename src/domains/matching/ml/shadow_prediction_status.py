from enum import Enum


class ShadowPredictionStatus(
    str,
    Enum,
):
    DISABLED = "DISABLED"
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    READY = "READY"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"