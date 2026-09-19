import pytest

from app.services.highlights import (
    Highlight,
    HighlightError,
    add,
    clamp_to_text,
    from_stored,
    remove,
)


def spans(highlights):
    return [(h.field, h.start, h.end) for h in highlights]


def test_add_returns_the_span_with_an_id():
    result = add([], "abstract", 4, 10, text_length=50)
    assert spans(result) == [("abstract", 4, 10)]
    assert result[0].id


def test_disjoint_spans_stay_separate():
    result = add(add([], "abstract", 0, 5, 50), "abstract", 20, 30, 50)
    assert spans(result) == [("abstract", 0, 5), ("abstract", 20, 30)]


def test_overlapping_spans_merge_into_one():
    result = add(add([], "abstract", 0, 10, 50), "abstract", 5, 20, 50)
    assert spans(result) == [("abstract", 0, 20)]


def test_touching_spans_merge():
    # Two passes of a highlighter over adjoining text read as one mark.
    result = add(add([], "abstract", 0, 5, 50), "abstract", 5, 9, 50)
    assert spans(result) == [("abstract", 0, 9)]


def test_a_span_swallowing_several_merges_all_of_them():
    existing = add(
        add(add([], "abstract", 0, 5, 50), "abstract", 10, 15, 50), "abstract", 20, 25, 50
    )
    result = add(existing, "abstract", 2, 30, 50)
    assert spans(result) == [("abstract", 0, 30)]


def test_fields_do_not_merge_with_each_other():
    result = add(add([], "title", 0, 10, 20), "abstract", 0, 10, 50)
    assert spans(result) == [("abstract", 0, 10), ("title", 0, 10)]


def test_a_span_past_the_end_is_clamped():
    result = add([], "abstract", 5, 900, text_length=20)
    assert spans(result) == [("abstract", 5, 20)]


def test_an_empty_span_is_rejected():
    with pytest.raises(HighlightError):
        add([], "abstract", 7, 7, text_length=20)


def test_a_span_starting_past_the_end_is_rejected():
    with pytest.raises(HighlightError):
        add([], "abstract", 30, 40, text_length=20)


def test_highlighting_a_field_with_no_text_is_rejected():
    with pytest.raises(HighlightError):
        add([], "abstract", 0, 5, text_length=0)


def test_an_unknown_field_is_rejected():
    with pytest.raises(HighlightError):
        add([], "notes", 0, 5, text_length=50)


def test_remove_takes_only_the_one_asked_for():
    existing = add(add([], "abstract", 0, 5, 50), "abstract", 20, 30, 50)
    target = next(h for h in existing if h.start == 20)
    assert spans(remove(existing, target.id)) == [("abstract", 0, 5)]


def test_removing_something_that_is_not_there_is_an_error():
    with pytest.raises(HighlightError):
        remove(add([], "abstract", 0, 5, 50), "nope")


def test_malformed_stored_entries_are_skipped_not_fatal():
    stored = [
        {"id": "a", "field": "abstract", "start": 0, "end": 5},
        {"id": "b", "field": "abstract", "start": 5, "end": 5},  # empty
        {"id": "c", "field": "notes", "start": 0, "end": 5},  # not highlightable
        {"id": "d", "field": "abstract", "start": "x", "end": 5},  # unparseable
        "not a dict",
        {"field": "abstract", "start": 0, "end": 5},  # no id
    ]
    assert spans(from_stored(stored)) == [("abstract", 0, 5)]


def test_clamp_drops_and_shortens_spans_that_no_longer_fit():
    # An abstract edited down to 10 characters.
    existing = [
        Highlight(id="a", field="abstract", start=0, end=4),
        Highlight(id="b", field="abstract", start=8, end=40),
        Highlight(id="c", field="abstract", start=30, end=40),
    ]
    assert spans(clamp_to_text(existing, {"abstract": 10})) == [
        ("abstract", 0, 4),
        ("abstract", 8, 10),
    ]
