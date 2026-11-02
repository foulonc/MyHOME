"""Event-session watchdog: a silent session is reopened, a failed reopen is retried.

Needs Home Assistant and OWNd importable, e.g. inside the HA container:
    python3 tests/test_event_watchdog.py
"""
import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from custom_components.myhome import gateway  # noqa: E402


class HalfOpenSession:
    """Connects fine, then never delivers a frame: a socket a router forgot."""

    opened = 0

    def __init__(self, **_):
        pass

    async def connect(self):
        HalfOpenSession.opened += 1
        if HalfOpenSession.opened == 2:
            raise OSError("No route to host")  # router still rebooting
        return {"Success": True}

    async def get_next(self):
        await asyncio.sleep(3600)

    async def close(self):
        pass


async def main():
    gateway.OWNEventSession = HalfOpenSession
    gateway.EVENT_SILENCE_TIMEOUT = 0.05
    gateway.EVENT_RECONNECT_DELAY = 0.01

    handler = gateway.MyHOMEGatewayHandler.__new__(gateway.MyHOMEGatewayHandler)
    handler.gateway = SimpleNamespace(log_id="[test]")
    handler.listening_worker = SimpleNamespace(cancel=lambda: None)
    task = asyncio.create_task(handler.listening_loop())

    for _ in range(200):
        if HalfOpenSession.opened >= 3:
            break
        await asyncio.sleep(0.01)
    # 1: initial open, silent -> 2: reopen fails with OSError -> 3: retried
    assert HalfOpenSession.opened >= 3, f"only {HalfOpenSession.opened} connects"
    assert not task.done(), "listening loop died"

    handler._terminate_listener = True
    await asyncio.wait_for(task, 1)
    assert handler.is_connected is False
    print("ok")


asyncio.run(main())
