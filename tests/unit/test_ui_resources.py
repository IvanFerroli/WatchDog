from pathlib import Path

from watchdog.ui.resources import application_icon_path, staged_application_icon_path


def test_official_icon_is_available_from_source_checkout() -> None:
    icon_path = application_icon_path()

    assert icon_path.is_file()
    assert icon_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_icon_is_staged_in_local_data_directory(tmp_path: Path) -> None:
    staged = staged_application_icon_path(tmp_path)

    assert staged == tmp_path / "assets" / "alwaystrack.png"
    assert staged.read_bytes() == application_icon_path().read_bytes()
