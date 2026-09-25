#!/usr/bin/env python3
"""Start the backend (FastAPI) and frontend (Vite) together for local use.

Runs on Linux, macOS and Windows. The platform-specific parts are the
virtualenv layout (``Scripts`` vs ``bin``), locating ``npm`` (a ``.cmd``
shim on Windows), and how a child's whole process tree is torn down --
neither uvicorn nor Vite is the only process it spawns, so signalling the
direct child alone would leave a port bound after Ctrl+C.

Usage:
    python run.py                (or ./run.sh on macOS/Linux, run.cmd on Windows)
    python run.py --no-browser   start the servers without opening a window
"""

from __future__ import annotations

import argparse
import errno
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
IS_WINDOWS = os.name == "nt"

DEFAULT_BACKEND_PORT = 8000
DEFAULT_FRONTEND_PORT = 5173
# How far past the default to look before giving up on a tidy port number.
PORT_SEARCH_RANGE = 20
# How long to wait for the servers before opening a window at the app's URL.
SERVERS_READY_TIMEOUT_SECONDS = 40.0

SETUP_BACKEND = (
    "Backend not set up yet. From the repository root:\n"
    "  cd backend\n"
    "  uv sync\n"
    "  uv run alembic upgrade head\n"
    "(uv: https://docs.astral.sh/uv/getting-started/installation/)"
)
SETUP_FRONTEND = (
    "Frontend dependencies not installed. From the repository root:\n"
    "  cd frontend\n"
    "  npm install"
)


def venv_executable(name: str) -> Path:
    """Path to an executable inside ``backend/.venv``.

    Windows virtualenvs put executables in ``Scripts`` with an ``.exe``
    suffix; every other platform uses ``bin`` with no suffix.
    """
    if IS_WINDOWS:
        return BACKEND_DIR / ".venv" / "Scripts" / f"{name}.exe"
    return BACKEND_DIR / ".venv" / "bin" / name


def npm_executable() -> str | None:
    """Resolve npm on PATH.

    On Windows npm is a ``npm.cmd`` shim rather than a real executable, and
    ``shutil.which`` is what turns the bare name into the full path that
    subprocess can launch.
    """
    return shutil.which("npm")


# Both loopback families have to be checked. Vite listens on "localhost",
# which Node resolves to ::1, while uvicorn takes 127.0.0.1 -- so probing only
# one family happily reports a port as free that the other server is already
# sitting on.
LOOPBACKS = ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1"))
# Errors that mean "this host has no such loopback", not "something is there".
_FAMILY_UNAVAILABLE = {errno.EAFNOSUPPORT, errno.EADDRNOTAVAIL, errno.EPROTONOSUPPORT}


def port_is_free(port: int) -> bool:
    """Whether a server could bind this port on loopback right now.

    Deliberately without SO_REUSEADDR: we want to know whether something is
    *already listening*, which is exactly what that option would paper over.
    """
    for family, host in LOOPBACKS:
        try:
            with socket.socket(family, socket.SOCK_STREAM) as probe:
                probe.bind((host, port))
        except OSError as error:
            if error.errno in _FAMILY_UNAVAILABLE:
                continue
            return False
    return True


def pick_port(preferred: int, taken: set[int]) -> int:
    """The preferred port if it is free, else the next free one after it.

    Another instance of the app, or anything else on 8000/5173, otherwise
    leaves the servers unable to start at all. Falling forward keeps a second
    copy of the app usable instead of failing on a port collision.

    There is a small race here -- the port is free when we look and could be
    taken by the time the child binds it -- but the child then fails loudly
    and the launcher stops the other half rather than leaving it half-up.
    """
    for port in range(preferred, preferred + PORT_SEARCH_RANGE):
        if port not in taken and port_is_free(port):
            return port
    # Nothing tidy was free; let the OS hand out whatever it has.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def wait_for_servers(urls: list[str], processes: list[subprocess.Popen]) -> bool:
    """Block until every URL answers, or it becomes pointless to wait.

    Both halves have to be up, not just the one whose URL the window opens at.
    Vite is ready in a fraction of a second while uvicorn still has its imports
    and the database to get through, so a browser sent to the app the moment
    the dev server answers lands on a page whose first API calls are proxied to
    nothing -- including the one that arranges for these servers to stop when
    that window is closed.
    """
    deadline = time.monotonic() + SERVERS_READY_TIMEOUT_SECONDS
    pending = list(urls)
    while pending:
        if time.monotonic() >= deadline:
            return False
        if any(process.poll() is not None for process in processes):
            return False
        try:
            with urllib.request.urlopen(pending[0], timeout=1):
                pending.pop(0)
        except (urllib.error.URLError, OSError):
            time.sleep(0.3)
    return True


class _ChildExited(Exception):
    """Internal: one of the two servers exited, so tear the other one down."""


def install_shutdown_handler() -> None:
    """Treat SIGTERM like Ctrl+C.

    Without this, closing the terminal or `kill`-ing the launcher would leave
    uvicorn and Vite running and their ports bound.
    """

    def handler(_signum: int, _frame: object) -> NoReturn:
        raise KeyboardInterrupt

    try:
        signal.signal(signal.SIGTERM, handler)
    except ValueError:
        # Not running in the main thread; Ctrl+C handling still applies.
        pass


def fail(message: str) -> NoReturn:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def spawn(
    command: list[str], cwd: Path, env: dict[str, str] | None = None
) -> subprocess.Popen:
    """Start a long-running child in its own process group.

    The new group is what lets `stop` later take down the child *and* the
    processes it spawned, and on Windows it also keeps our own Ctrl+C from
    reaching the children before we have had a chance to shut them down in
    order.
    """
    kwargs: dict = {"cwd": str(cwd)}
    if env is not None:
        kwargs["env"] = {**os.environ, **env}
    if IS_WINDOWS:
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(command, **kwargs)


def stop(process: subprocess.Popen) -> None:
    """Terminate a child and everything it spawned."""
    if process.poll() is not None:
        return
    if IS_WINDOWS:
        # /T walks the child tree, which is the only reliable way to reach
        # the node and python processes started underneath the shims.
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            capture_output=True,
            check=False,
        )
    else:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="start the servers without opening a window (they then stop only on Ctrl+C)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    install_shutdown_handler()

    uvicorn = venv_executable("uvicorn")
    if not uvicorn.exists():
        fail(SETUP_BACKEND)

    if not (FRONTEND_DIR / "node_modules").is_dir():
        fail(SETUP_FRONTEND)

    npm = npm_executable()
    if npm is None:
        fail("npm not found on PATH. Install Node.js 20+ from https://nodejs.org/.")

    backend_port = pick_port(DEFAULT_BACKEND_PORT, taken=set())
    frontend_port = pick_port(DEFAULT_FRONTEND_PORT, taken={backend_port})
    frontend_url = f"http://localhost:{frontend_port}"

    processes: list[subprocess.Popen] = []
    try:
        processes.append(
            spawn(
                [str(uvicorn), "app.main:app", "--port", str(backend_port)],
                BACKEND_DIR,
                env={
                    # The dev server proxies /api, so requests are same-origin
                    # and CORS never applies -- but keep the allowed origin in
                    # step with the port actually in use for anything hitting
                    # the API directly from the browser.
                    "LRA_CORS_ORIGINS": f"{frontend_url},http://127.0.0.1:{frontend_port}",
                    # Opt the backend into stopping when the app's window goes
                    # away. Only the launcher sets this, so a hand-started
                    # uvicorn keeps running regardless of any browser.
                    "LRA_SESSION_WATCH": "0" if args.no_browser else "1",
                },
            )
        )
        processes.append(
            spawn(
                # --strictPort: without it Vite silently walks to another port
                # of its own choosing, and the URL printed below would be wrong.
                [npm, "run", "dev", "--", "--port", str(frontend_port), "--strictPort"],
                FRONTEND_DIR,
                env={"LRA_API_PORT": str(backend_port)},
            )
        )
    except OSError as error:
        for process in processes:
            stop(process)
        fail(f"Failed to start: {error}")

    # flush: stdout is block-buffered when the launcher's output is piped or
    # redirected, which would otherwise hold these lines back until exit.
    if backend_port != DEFAULT_BACKEND_PORT or frontend_port != DEFAULT_FRONTEND_PORT:
        print("Default port(s) already in use; falling forward.", flush=True)
    print(f"Backend:  http://localhost:{backend_port}/docs", flush=True)
    print(f"Frontend: {frontend_url}", flush=True)

    if args.no_browser:
        print("Press Ctrl+C to stop both.", flush=True)
    else:
        backend_health = f"http://127.0.0.1:{backend_port}/api/health"
        if wait_for_servers([backend_health, frontend_url], processes):
            webbrowser.open(frontend_url)
        else:
            print(
                "Servers did not both come up in time; open the URL above yourself.",
                flush=True,
            )
        print("Close the window, or press Ctrl+C here, to stop both.", flush=True)

    exit_code = 0
    try:
        # Poll rather than `wait`, so that either process exiting on its own
        # (a port already in use, say) brings the other one down too instead
        # of leaving half the app running.
        while True:
            for process in processes:
                if process.poll() is not None:
                    exit_code = process.returncode or 0
                    raise _ChildExited
            time.sleep(0.3)
    except (KeyboardInterrupt, _ChildExited):
        pass
    finally:
        print("\nStopping...", flush=True)
        for process in processes:
            stop(process)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
