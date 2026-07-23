from watchdog.ui.resources import application_icon_path


def test_official_icon_is_available_from_source_checkout() -> None:
    icon_path = application_icon_path()

    assert icon_path.is_file()
    assert icon_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
