"""The documentation screenshots' example review still builds through the API.

``scripts/take_screenshots.py`` is only ever run by hand, so an API change that
breaks its seeding -- a moved route, a stricter validator, a tag weight that is
no longer allowed -- would otherwise go unnoticed until the next time someone
retakes the pictures.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import screenshot_data as demo  # noqa: E402
from take_screenshots import seed  # noqa: E402


def test_example_review_seeds_through_the_api(client):
    seeded = seed(client)
    base = f"/api/projects/{seeded.project_id}"

    papers = client.get(f"{base}/papers").json()
    assert [paper["title"] for paper in papers] == [paper.title for paper in demo.PAPERS]

    # The workspace pictures open on the paper the seeding last viewed.
    current = papers[demo.CURRENT_PAPER - 1]
    assert client.get(base).json()["last_viewed_paper_id"] == current["id"]
    assert client.get(f"{base}/papers/{current['id']}").json()["highlights"]

    # A complete plan, so the "Review plan" button carries no incomplete dot.
    plan = client.get(f"{base}/plan").json()
    assert plan["filled"] == plan["total"]

    fields = {field["name"]: field for field in client.get(f"{base}/fields").json()}
    assert fields[demo.CUSTOM_FIELD]["id"] == seeded.custom_field_id
