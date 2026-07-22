from __future__ import annotations

import pytest

from watchdog.application.single_instance import AlreadyRunningError, SingleInstanceLock


def test_single_instance_lock_blocks_second_process_lock(tmp_path) -> None:
    first = SingleInstanceLock(tmp_path / "watchdog.lock")
    second = SingleInstanceLock(tmp_path / "watchdog.lock")
    first.acquire()
    try:
        with pytest.raises(AlreadyRunningError):
            second.acquire()
    finally:
        first.release()
    second.acquire()
    second.release()
