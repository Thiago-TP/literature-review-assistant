from app.services.dedup import (
    ExistingPaperKey,
    classify,
    classify_batch,
    normalize_doi,
    normalize_title,
)


def test_normalize_doi_strips_url_prefixes():
    assert normalize_doi("https://doi.org/10.1016/J.CES.2025.122416") == "10.1016/j.ces.2025.122416"
    assert normalize_doi("http://dx.doi.org/10.1/X") == "10.1/x"
    assert normalize_doi("doi:10.1/X") == "10.1/x"
    assert normalize_doi("  10.1/X/  ") == "10.1/x"
    assert normalize_doi(None) is None
    assert normalize_doi("") is None


def test_normalize_title_strips_punctuation_and_case():
    assert normalize_title("Attention Is All You Need!") == "attention is all you need"
    assert normalize_title("A, B: C-D") == "a b cd"
    assert normalize_title("  multiple   spaces  ") == "multiple spaces"
    assert normalize_title(None) == ""


def test_classify_matches_by_doi_even_with_different_title():
    existing = [
        ExistingPaperKey(
            paper_id=1,
            title="Original Title",
            doi_normalized="10.1/x",
            title_normalized="original title",
        )
    ]
    result = classify("A Completely Different Title", "https://doi.org/10.1/X", existing)
    assert result.is_duplicate
    assert result.reason == "doi"
    assert result.matched_paper_id == 1
    assert result.default_action == "skip"


def test_classify_matches_by_title_when_no_doi_match():
    existing = [
        ExistingPaperKey(
            paper_id=2,
            title="Some Paper Title",
            doi_normalized=None,
            title_normalized="some paper title",
        )
    ]
    result = classify("Some Paper Title!!", None, existing)
    assert result.is_duplicate
    assert result.reason == "title"
    assert result.matched_paper_id == 2


def test_classify_new_paper_no_match():
    existing = [
        ExistingPaperKey(
            paper_id=3, title="Other", doi_normalized="10.1/y", title_normalized="other"
        )
    ]
    result = classify("Brand New Paper", "10.1/z", existing)
    assert not result.is_duplicate
    assert result.default_action == "add"


def test_classify_batch_catches_intra_batch_duplicates():
    rows = [("Paper One", "10.1/a"), ("paper one", "10.1/a"), ("Paper Two", None)]
    results = classify_batch(rows, existing=[])
    assert not results[0].is_duplicate
    assert results[1].is_duplicate
    assert results[1].reason == "doi"
    assert not results[2].is_duplicate
