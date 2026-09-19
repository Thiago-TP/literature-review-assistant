"""Endpoints the app's own page uses to say it is still open.

They exist whether or not the launcher is watching, so the client can ask once
and stay quiet when nobody is listening.
"""

from __future__ import annotations

from fastapi import APIRouter

from app import session_watch

router = APIRouter(prefix="/api/session", tags=["session"])


@router.get("/status")
def status() -> dict[str, bool]:
    """Whether anything will act on heartbeats from this client."""
    return {"watching": session_watch.WATCHING}


@router.post("/heartbeat", status_code=204)
def heartbeat() -> None:
    session_watch.state.beat()


@router.post("/closed", status_code=204)
def closed() -> None:
    """Sent as the page unloads. Only schedules a stop -- a reload's first
    heartbeat cancels it."""
    session_watch.state.mark_closed()
