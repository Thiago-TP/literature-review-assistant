from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile

from app.deps import SessionDep, get_project_or_404
from app.schemas import (
    DuplicateInfo,
    ImportCommitRequest,
    ImportCommitResponse,
    ImportPreviewResponse,
    ImportPreviewRow,
    LookupCandidate,
    LookupDoiRequest,
    LookupDoiResponse,
    LookupTitleRequest,
    LookupTitleResponse,
)
from app.services import crossref, dedup
from app.services.paper_repo import build_paper, existing_paper_keys, next_order_index
from app.services.xlsx_import import XlsxImportError, parse_xlsx

router = APIRouter(prefix="/api/projects/{project_id}", tags=["import"])


@router.post("/import/xlsx/preview", response_model=ImportPreviewResponse)
async def preview_xlsx_import(
    project_id: int, session: SessionDep, file: UploadFile
) -> ImportPreviewResponse:
    get_project_or_404(project_id, session)
    file_bytes = await file.read()
    try:
        parsed_rows = parse_xlsx(file_bytes)
    except XlsxImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    existing = existing_paper_keys(session, project_id)
    classifications = dedup.classify_batch([(row.title, row.doi) for row in parsed_rows], existing)

    rows = [
        ImportPreviewRow(
            row_index=index,
            title=parsed.title,
            abstract=parsed.abstract,
            doi=parsed.doi,
            authors=parsed.authors,
            year=parsed.year,
            source_title=parsed.source_title,
            raw_metadata=parsed.raw_metadata,
            is_duplicate=classification.is_duplicate,
            duplicate_reason=classification.reason,
            matched_paper_id=classification.matched_paper_id,
            matched_title=classification.matched_title,
            default_action=classification.default_action,
        )
        for index, (parsed, classification) in enumerate(
            zip(parsed_rows, classifications, strict=True)
        )
    ]
    duplicate_count = sum(1 for r in rows if r.is_duplicate)
    return ImportPreviewResponse(
        rows=rows, new_count=len(rows) - duplicate_count, duplicate_count=duplicate_count
    )


@router.post("/import/xlsx/commit", response_model=ImportCommitResponse)
def commit_xlsx_import(
    project_id: int, payload: ImportCommitRequest, session: SessionDep
) -> ImportCommitResponse:
    get_project_or_404(project_id, session)
    order_index = next_order_index(session, project_id)
    paper_ids: list[int] = []
    skipped_count = 0

    for row in payload.rows:
        action = payload.actions.get(row.row_index, row.default_action)
        if action != "add":
            skipped_count += 1
            continue
        paper = build_paper(
            project_id=project_id,
            title=row.title,
            abstract=row.abstract,
            doi=row.doi,
            authors=row.authors,
            year=row.year,
            source_title=row.source_title,
            source="xlsx_import",
            raw_metadata=row.raw_metadata,
            order_index=order_index,
        )
        order_index += 1
        session.add(paper)
        session.flush()
        paper_ids.append(paper.id)

    session.commit()
    return ImportCommitResponse(
        added_count=len(paper_ids), skipped_count=skipped_count, paper_ids=paper_ids
    )


def _to_candidate(work: crossref.CrossRefWork, existing) -> LookupCandidate:
    classification = dedup.classify(work.title, work.doi, existing)
    return LookupCandidate(
        title=work.title,
        doi=work.doi,
        abstract=work.abstract,
        abstract_available=work.abstract_available,
        authors=work.authors,
        year=work.year,
        source_title=work.source_title,
        score=work.score,
        raw_metadata=work.raw_metadata,
        duplicate=DuplicateInfo(
            is_duplicate=classification.is_duplicate,
            reason=classification.reason,
            matched_paper_id=classification.matched_paper_id,
            matched_title=classification.matched_title,
        ),
    )


@router.post("/papers/lookup/doi", response_model=LookupDoiResponse)
async def lookup_by_doi(
    project_id: int, payload: LookupDoiRequest, session: SessionDep
) -> LookupDoiResponse:
    get_project_or_404(project_id, session)
    try:
        work = await crossref.lookup_by_doi(payload.doi.strip())
    except crossref.CrossRefNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except crossref.CrossRefRequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    existing = existing_paper_keys(session, project_id)
    return LookupDoiResponse(candidate=_to_candidate(work, existing))


@router.post("/papers/lookup/title", response_model=LookupTitleResponse)
async def lookup_by_title(
    project_id: int, payload: LookupTitleRequest, session: SessionDep
) -> LookupTitleResponse:
    get_project_or_404(project_id, session)
    try:
        works = await crossref.search_by_title(payload.title.strip())
    except crossref.CrossRefRequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    existing = existing_paper_keys(session, project_id)
    return LookupTitleResponse(candidates=[_to_candidate(w, existing) for w in works])
