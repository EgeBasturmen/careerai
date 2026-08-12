from enum import Enum


class JobIngestionStatus(str, Enum):
    QUEUED = "QUEUED"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"