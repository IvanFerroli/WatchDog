"""Replaceable Slack Desktop adapter based on Windows UI Automation."""

from .activity import ActivitySelectors, PywinautoActivityReader
from .adapter import SlackUIAdapter
from .errors import AdapterErrorCode, SlackAdapterError
from .provider import PywinautoWindowProvider, SlackWindow, SlackWindowLifecycle

__all__ = [
    "ActivitySelectors",
    "AdapterErrorCode",
    "PywinautoActivityReader",
    "PywinautoWindowProvider",
    "SlackAdapterError",
    "SlackUIAdapter",
    "SlackWindow",
    "SlackWindowLifecycle",
]
