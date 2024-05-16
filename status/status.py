"""
Module to provide messages and helper methods for the different
steps in downloading a comic and processing it
"""
from enum import Enum


class Status(Enum):
    """
    Enum for the different steps
    """

    DOWNLOADING = "Downloading"
    CROPPING = "Cropping"
    ADDING_PAGES = "Adding Pages"
    EXPORTING = "Exporting PDF"
    COMPLETE = "Complete!"


def get_status_length() -> int:
    """
    returns length of the longest Status string
    """
    res = 0
    for status in Status:
        res = max(res, len(status.value))
    return res
