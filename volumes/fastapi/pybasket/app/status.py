from enum import Enum


class Status(str, Enum):
    ORDERED = "ordered"
    ACCEPTED = "accepted"
    STARTED = "started"
    FAILED = "failed"
    SUCCEEDED = "succeeded"
    EXCEEDED = "exceeded"
