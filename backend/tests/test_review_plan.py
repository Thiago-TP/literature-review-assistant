from app.services.review_plan import (
    PLAN_SECTIONS,
    count_written,
    is_written,
    plan_progress,
)


def test_is_written_rejects_nothing_and_whitespace():
    # Whitespace must not count, or the space bar clears the "incomplete" badge.
    assert is_written(None) is False
    assert is_written("") is False
    assert is_written("   \n\t ") is False
    assert is_written("Because nobody has compared these two approaches.") is True


def test_count_written_ignores_the_blanks():
    assert count_written([None, "", "  ", "real text", "more"]) == 2


def test_plan_progress_of_an_untouched_review():
    progress = plan_progress([None] * 5, [None, None], [None, None, None])
    assert progress.filled == 0
    assert progress.total == 10
    assert progress.is_complete is False


def test_plan_progress_counts_sections_fields_and_adherence_together():
    progress = plan_progress(
        ["why", None, None, None, None],
        ["what this field asks", None],
        ["insufficient means", None, None],
    )
    assert progress.filled == 3
    assert progress.total == 10


def test_plan_progress_is_complete_only_when_everything_is_written():
    almost = plan_progress(["a"] * 5, ["b", "c"], ["d", "e", None])
    assert almost.is_complete is False

    done = plan_progress(["a"] * 5, ["b", "c"], ["d", "e", "f"])
    assert done.filled == done.total == 10
    assert done.is_complete is True


def test_extra_fields_raise_the_total():
    """Adding a custom field adds one more thing to describe, so a plan that
    was complete becomes incomplete rather than silently staying done."""
    before = plan_progress(["a"] * 5, ["b", "c"], ["d", "e", "f"])
    after = plan_progress(["a"] * 5, ["b", "c", None], ["d", "e", "f"])
    assert before.is_complete is True
    assert after.total == before.total + 1
    assert after.is_complete is False


def test_plan_sections_match_the_columns_they_are_read_from():
    # The router builds `plan_<section>` attribute names from these.
    assert PLAN_SECTIONS == ("purpose", "scope", "search", "weights", "other")
