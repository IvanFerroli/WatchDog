import json

import pytest

from watchdog.core.config import AppConfig, ConfigError


def test_default_config_round_trips_and_default_file_is_valid() -> None:
    config = AppConfig.load("config/default.json")
    assert AppConfig.from_json(config.to_json()) == config
    assert json.loads(config.to_json())["slack"]["process_names"] == ["slack.exe"]


@pytest.mark.parametrize(
    "patch, message",
    [
        ({"watchdog": {"poll_interval_ms": 0}}, "positive integer"),
        ({"watchdog": {"enabled": 1}}, "boolean"),
        ({"slack": {"direct_mention_labels": []}}, "must not be empty"),
        ({"logging": {"level": "verbose"}}, "invalid"),
        ({"unexpected": True}, "unknown root"),
    ],
)
def test_invalid_config_is_rejected(patch: dict[str, object], message: str) -> None:
    with pytest.raises(ConfigError, match=message):
        AppConfig.from_dict(patch)
