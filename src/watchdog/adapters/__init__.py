"""External event adapters."""

from .composite import CompositeEventAdapter, SourceFailure
from .slack_ui import (
    ActivitySelectors,
    AdapterErrorCode,
    PywinautoActivityReader,
    PywinautoWindowProvider,
    SlackAdapterError,
    SlackUIAdapter,
    SlackWindowLifecycle,
)
from .windows_notifications import (
    SlackDirectMessagePolicy,
    UserNotificationListenerSource,
    WindowsNotificationError,
    WindowsNotificationErrorCode,
    WindowsNotificationRecord,
)

__all__ = [
    "ActivitySelectors",
    "AdapterErrorCode",
    "CompositeEventAdapter",
    "PywinautoActivityReader",
    "PywinautoWindowProvider",
    "SlackAdapterError",
    "SlackDirectMessagePolicy",
    "SlackUIAdapter",
    "SlackWindowLifecycle",
    "SourceFailure",
    "UserNotificationListenerSource",
    "WindowsNotificationError",
    "WindowsNotificationErrorCode",
    "WindowsNotificationRecord",
]
