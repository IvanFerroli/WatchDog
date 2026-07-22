"""PyInstaller entrypoint using package-absolute imports."""

from watchdog.application.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
