import json

import pytest

from watchdog.core.config import AppConfig, ConfigError


def test_default_config_round_trips_and_default_file_is_valid() -> None:
    config = AppConfig.load("config/default.json")
    assert AppConfig.from_json(config.to_json()) == config
    assert json.loads(config.to_json())["slack"]["process_names"] == ["slack.exe"]
    assert config.notification.direct_mentions_enabled is True
    assert config.notification.direct_messages_enabled is True


def test_notification_category_preferences_are_independently_configurable() -> None:
    config = AppConfig.from_dict(
        {
            "notification": {
                "direct_mentions_enabled": False,
                "direct_messages_enabled": True,
            }
        }
    )

    assert config.notification.direct_mentions_enabled is False
    assert config.notification.direct_messages_enabled is True


@pytest.mark.parametrize(
    "patch, message",
    [
        ({"watchdog": {"poll_interval_ms": 0}}, "positive integer"),
        ({"watchdog": {"enabled": 1}}, "boolean"),
        ({"notification": {"direct_messages_enabled": "yes"}}, "boolean"),
        ({"slack": {"direct_mention_labels": []}}, "must not be empty"),
        ({"logging": {"level": "verbose"}}, "invalid"),
        ({"unexpected": True}, "unknown root"),
    ],
)
def test_invalid_config_is_rejected(patch: dict[str, object], message: str) -> None:
    with pytest.raises(ConfigError, match=message):
        AppConfig.from_dict(patch)
