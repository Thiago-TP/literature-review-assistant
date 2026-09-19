"""Thin client for the CrossRef public API (no API key required).

Used to fetch metadata for a single paper added by DOI or title, so the user
never has to hand-type title/abstract/authors for a one-off addition.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import httpx

from app.config import CROSSREF_BASE_URL, CROSSREF_MAILTO, CROSSREF_TIMEOUT_SECONDS

_JATS_TAG_RE = re.compile(r"<[^<]+?>")


class CrossRefNotFoundError(Exception):
    pass


class CrossRefRequestError(Exception):
    pass


@dataclass
class CrossRefWork:
    title: str
    doi: str | None
    abstract: str | None
    abstract_available: bool
    authors: str | None
    year: int | None
    source_title: str | None
    raw_metadata: dict
    score: float | None = None


def _user_agent() -> str:
    return f"LiteratureReviewAssistant/1.0 (mailto:{CROSSREF_MAILTO})"


def _strip_jats(text: str | None) -> str | None:
    if not text:
        return None
    return _JATS_TAG_RE.sub("", text).strip() or None


def _extract_year(message: dict) -> int | None:
    for key in ("published-print", "published-online", "issued", "created"):
        date_parts = message.get(key, {}).get("date-parts")
        if date_parts and date_parts[0] and date_parts[0][0]:
            return int(date_parts[0][0])
    return None


def _extract_authors(message: dict) -> str | None:
    authors = message.get("author") or []
    names = [
        f"{author.get('given', '')} {author.get('family', '')}".strip()
        for author in authors
        if author.get("family")
    ]
    return "; ".join(names) or None


def _message_to_work(message: dict, score: float | None = None) -> CrossRefWork:
    titles = message.get("title") or []
    abstract = _strip_jats(message.get("abstract"))
    return CrossRefWork(
        title=titles[0] if titles else "(untitled)",
        doi=message.get("DOI"),
        abstract=abstract,
        abstract_available=abstract is not None,
        authors=_extract_authors(message),
        year=_extract_year(message),
        source_title=(message.get("container-title") or [None])[0],
        raw_metadata=message,
        score=score,
    )


async def lookup_by_doi(doi: str) -> CrossRefWork:
    url = f"{CROSSREF_BASE_URL}/works/{doi}"
    async with httpx.AsyncClient(timeout=CROSSREF_TIMEOUT_SECONDS) as client:
        try:
            response = await client.get(url, headers={"User-Agent": _user_agent()})
        except httpx.HTTPError as exc:
            raise CrossRefRequestError(str(exc)) from exc

    if response.status_code == 404:
        raise CrossRefNotFoundError(f"DOI not found in CrossRef: {doi}")
    if response.status_code >= 400:
        raise CrossRefRequestError(f"CrossRef returned HTTP {response.status_code}")

    return _message_to_work(response.json()["message"])


async def search_by_title(title: str, rows: int = 5) -> list[CrossRefWork]:
    url = f"{CROSSREF_BASE_URL}/works"
    params = {"query.bibliographic": title, "rows": rows}
    async with httpx.AsyncClient(timeout=CROSSREF_TIMEOUT_SECONDS) as client:
        try:
            response = await client.get(url, params=params, headers={"User-Agent": _user_agent()})
        except httpx.HTTPError as exc:
            raise CrossRefRequestError(str(exc)) from exc

    if response.status_code >= 400:
        raise CrossRefRequestError(f"CrossRef returned HTTP {response.status_code}")

    items = response.json()["message"].get("items", [])
    return [_message_to_work(item, score=item.get("score")) for item in items]
