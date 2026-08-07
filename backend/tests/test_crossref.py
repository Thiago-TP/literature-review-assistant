import httpx
import pytest

from app.services import crossref

_RealAsyncClient = httpx.AsyncClient


def _patch_transport(monkeypatch, handler):
    def fake_async_client(**kwargs):
        kwargs.pop("transport", None)
        return _RealAsyncClient(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client)


@pytest.mark.asyncio
async def test_lookup_by_doi_success(monkeypatch):
    message = {
        "title": ["A Great Paper"],
        "DOI": "10.1/x",
        "abstract": "<jats:p>Some <jats:italic>abstract</jats:italic> text.</jats:p>",
        "author": [{"given": "Ada", "family": "Lovelace"}],
        "published-print": {"date-parts": [[2020]]},
        "container-title": ["Journal of Things"],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/works/10.1/x"
        return httpx.Response(200, json={"message": message})

    _patch_transport(monkeypatch, handler)

    work = await crossref.lookup_by_doi("10.1/x")
    assert work.title == "A Great Paper"
    assert work.abstract == "Some abstract text."
    assert work.abstract_available
    assert work.authors == "Ada Lovelace"
    assert work.year == 2020
    assert work.source_title == "Journal of Things"


@pytest.mark.asyncio
async def test_lookup_by_doi_not_found(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    _patch_transport(monkeypatch, handler)

    with pytest.raises(crossref.CrossRefNotFoundError):
        await crossref.lookup_by_doi("10.1/missing")


@pytest.mark.asyncio
async def test_lookup_by_doi_missing_abstract(monkeypatch):
    message = {"title": ["No Abstract Here"], "DOI": "10.1/y"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"message": message})

    _patch_transport(monkeypatch, handler)

    work = await crossref.lookup_by_doi("10.1/y")
    assert work.abstract is None
    assert not work.abstract_available


@pytest.mark.asyncio
async def test_search_by_title_returns_multiple_candidates(monkeypatch):
    items = [
        {"title": ["Candidate One"], "DOI": "10.1/a", "score": 90.0},
        {"title": ["Candidate Two"], "DOI": "10.1/b", "score": 80.0},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        assert "query.bibliographic" in str(request.url)
        return httpx.Response(200, json={"message": {"items": items}})

    _patch_transport(monkeypatch, handler)

    works = await crossref.search_by_title("candidate")
    assert len(works) == 2
    assert works[0].title == "Candidate One"
    assert works[0].score == 90.0
