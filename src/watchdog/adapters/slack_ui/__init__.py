"""Replaceable Slack Desktop adapter based on Windows UI Automation."""

from .activity import ActivitySelectors, PywinautoActivityReader
from .adapter import SlackUIAdapter
from .errors import AdapterErrorCode, SlackAdapterError
from .navigation import PywinautoActivityNavigator
from .provider import PywinautoWindowProvider, SlackWindow, SlackWindowLifecycle

__all__ = [
    "ActivitySelectors",
    "AdapterErrorCode",
    "PywinautoActivityReader",
    "PywinautoActivityNavigator",
    "PywinautoWindowProvider",
    "SlackAdapterError",
    "SlackUIAdapter",
    "SlackWindow",
    "SlackWindowLifecycle",
]
