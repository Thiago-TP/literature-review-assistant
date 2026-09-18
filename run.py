#!/usr/bin/env python3
"""Start the backend (FastAPI) and frontend (Vite) together for local use.

Runs on Linux, macOS and Windows. The platform-specific parts are the
virtualenv layout (``Scripts`` vs ``bin``), locating ``npm`` (a ``.cmd``
shim on Windows), and how a child's whole process tree is torn down --
neither uvicorn nor Vite is the only process it spawns, so signalling the
direct child alone would leave a port bound after Ctrl+C.

Usage:
    python run.py          (or ./run.sh on macOS/Linux, run.cmd on Windows)
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
IS_WINDOWS = os.name == "nt"

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

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


def spawn(command: list[str], cwd: Path) -> subprocess.Popen:
    """Start a long-running child in its own process group.

    The new group is what lets `stop` later take down the child *and* the
    processes it spawned, and on Windows it also keeps our own Ctrl+C from
    reaching the children before we have had a chance to shut them down in
    order.
    """
    kwargs: dict = {"cwd": str(cwd)}
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


def main() -> int:
    install_shutdown_handler()

    uvicorn = venv_executable("uvicorn")
    if not uvicorn.exists():
        fail(SETUP_BACKEND)

    if not (FRONTEND_DIR / "node_modules").is_dir():
        fail(SETUP_FRONTEND)

    npm = npm_executable()
    if npm is None:
        fail("npm not found on PATH. Install Node.js 20+ from https://nodejs.org/.")

    processes: list[subprocess.Popen] = []
    try:
        processes.append(
            spawn([str(uvicorn), "app.main:app", "--port", "8000"], BACKEND_DIR)
        )
        processes.append(spawn([npm, "run", "dev"], FRONTEND_DIR))
    except OSError as error:
        for process in processes:
            stop(process)
        fail(f"Failed to start: {error}")

    # flush: stdout is block-buffered when the launcher's output is piped or
    # redirected, which would otherwise hold these lines back until exit.
    print(f"Backend:  {BACKEND_URL}/docs", flush=True)
    print(f"Frontend: {FRONTEND_URL}", flush=True)
    print("Press Ctrl+C to stop both.", flush=True)

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
