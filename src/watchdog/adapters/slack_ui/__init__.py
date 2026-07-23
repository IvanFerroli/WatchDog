"""Replaceable Slack Desktop adapter based on Windows UI Automation."""

from .activity import ActivitySelectors, PywinautoActivityReader
from .adapter import SlackUIAdapter
from .errors import AdapterErrorCode, SlackAdapterError
from .event_opener import PywinautoSlackEventOpener, SlackOpenResult
from .navigation import PywinautoActivityNavigator
from .provider import PywinautoWindowProvider, SlackWindow, SlackWindowLifecycle

__all__ = [
    "ActivitySelectors",
    "AdapterErrorCode",
    "PywinautoActivityReader",
    "PywinautoActivityNavigator",
    "PywinautoSlackEventOpener",
    "PywinautoWindowProvider",
    "SlackAdapterError",
    "SlackOpenResult",
    "SlackUIAdapter",
    "SlackWindow",
    "SlackWindowLifecycle",
]
