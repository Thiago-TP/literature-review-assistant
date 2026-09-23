"""Stop the server when the app's browser window goes away.

Only active when the launcher asks for it (``LRA_SESSION_WATCH=1``), so running
``uvicorn app.main:app`` by hand -- or pointing anything else at the API -- is
completely unaffected.

Two signals, because neither alone is enough:

* The page beacons ``/api/session/closed`` as it unloads. That is immediate but
  indistinguishable from a reload, so it only *schedules* a stop a few seconds
  out, which the reloaded page's first heartbeat cancels.
* The page heartbeats while it is open. That is the backstop for a browser that
  crashed or was force-quit and never got to send a beacon. Its grace period
  has to clear a minute, because browsers throttle timers in hidden tabs to
  roughly once a minute -- a backgrounded window is still an open window.

Nothing happens until the first heartbeat arrives, so a launcher whose browser
never opened stays up rather than exiting on its own.
"""

from __future__ import annotations

import os
import signal
import threading
import time

WATCHING = os.environ.get("LRA_SESSION_WATCH") == "1"

# Generous enough to clear the ~60s timer throttling browsers apply to hidden
# tabs; the beacon path is what makes an ordinary close feel immediate.
HEARTBEAT_GRACE_SECONDS = float(os.environ.get("LRA_SESSION_GRACE", "90"))
# Long enough for a reload to come back and cancel the stop.
CLOSE_GRACE_SECONDS = float(os.environ.get("LRA_SESSION_CLOSE_GRACE", "2"))
POLL_SECONDS = 1.0
# If a graceful stop does not take effect, stop being polite.
FORCE_EXIT_AFTER_SECONDS = 10.0


class _SessionState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_seen: float | None = None
        self._closing_since: float | None = None

    def beat(self) -> None:
        with self._lock:
            self._last_seen = time.monotonic()
            self._closing_since = None

    def mark_closed(self) -> None:
        with self._lock:
            # Ignore a beacon from a client we never saw heartbeat: it cannot
            # be the window this launcher opened.
            if self._last_seen is not None and self._closing_since is None:
                self._closing_since = time.monotonic()

    def should_stop(self) -> bool:
        with self._lock:
            if self._last_seen is None:
                return False
            now = time.monotonic()
            if self._closing_since is not None:
                # Timed from the beacon, not from the last heartbeat: a reload
                # that happens late in the heartbeat cycle must still get the
                # full grace period to come back and check in, and `beat`
                # clears this the moment it does.
                return now - self._closing_since >= CLOSE_GRACE_SECONDS
            return now - self._last_seen >= HEARTBEAT_GRACE_SECONDS


state = _SessionState()


def _stop_server() -> None:
    print("Frontend window closed; stopping.", flush=True)
    try:
        # SIGINT is what uvicorn installs a graceful-shutdown handler for, and
        # raise_signal reaches it on Windows too.
        signal.raise_signal(signal.SIGINT)
    except Exception:
        os._exit(0)
    time.sleep(FORCE_EXIT_AFTER_SECONDS)
    os._exit(0)


def _watch() -> None:
    while True:
        time.sleep(POLL_SECONDS)
        if state.should_stop():
            _stop_server()
            return


def start() -> None:
    """Begin watching, if the launcher asked for it."""
    if not WATCHING:
        return
    threading.Thread(target=_watch, name="session-watch", daemon=True).start()
