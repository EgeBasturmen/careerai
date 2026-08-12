from enum import Enum


class ResumeStatus(
    str,
    Enum,
):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"