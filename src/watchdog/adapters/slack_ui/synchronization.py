"""Process-local coordination for Slack UI Automation calls."""

from __future__ import annotations

from threading import RLock

SLACK_UI_AUTOMATION_LOCK = RLock()
