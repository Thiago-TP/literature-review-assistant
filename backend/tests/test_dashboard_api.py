def test_dashboard_on_empty_project(client, project):
    resp = client.get(f"/api/projects/{project['id']}/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_papers"] == 0
    assert body["fully_tagged_count"] == 0
    assert body["rated_count"] == 0
    assert body["with_notes_count"] == 0
    assert body["average_rating"] is None
    assert body["average_score"] == 0
    assert body["tag_distribution"] == []
    assert body["top_papers"] == []


def test_dashboard_aggregates_tags_ratings_and_scores(client, project):
    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    adherence = next(f for f in fields if f["name"] == "Adherence")
    sufficient = next(o for o in adherence["options"] if o["value"] == "Sufficient")
    client.patch(
        f"/api/projects/{project['id']}/fields/{adherence['id']}/options/{sufficient['id']}",
        json={"weight": 2},
    )

    paper_a = client.post(f"/api/projects/{project['id']}/papers", json={"title": "A"}).json()[
        "paper"
    ]
    paper_b = client.post(f"/api/projects/{project['id']}/papers", json={"title": "B"}).json()[
        "paper"
    ]

    client.post(f"/api/projects/{project['id']}/papers/{paper_a['id']}/tags/{sufficient['id']}")
    client.put(f"/api/projects/{project['id']}/papers/{paper_a['id']}/rating", json={"rating": 5})
    client.put(f"/api/projects/{project['id']}/papers/{paper_b['id']}/rating", json={"rating": 1})

    resp = client.get(f"/api/projects/{project['id']}/dashboard")
    body = resp.json()

    assert body["total_papers"] == 2
    assert body["rated_count"] == 2
    assert body["average_rating"] == 3
    assert body["average_score"] == ((2 + 5) + 1) / 2

    sufficient_entry = next(
        e for e in body["tag_distribution"] if e["option_id"] == sufficient["id"]
    )
    assert sufficient_entry["count"] == 1
    assert sufficient_entry["weight"] == 2
    assert sufficient_entry["field_name"] == "Adherence"

    assert body["top_papers"][0]["id"] == paper_a["id"]
    assert body["top_papers"][0]["score"] == 7


def test_dashboard_tag_distribution_shows_full_path_for_nested_tags(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    topic = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options", json={"value": "Topic"}
    ).json()
    subtopic = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options",
        json={"value": "Sub", "parent_option_id": topic["id"]},
    ).json()
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]
    client.post(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{subtopic['id']}")

    body = client.get(f"/api/projects/{project['id']}/dashboard").json()
    entry = next(e for e in body["tag_distribution"] if e["option_id"] == subtopic["id"])
    assert entry["option_path"] == "Topic > Sub"


def test_dashboard_fully_tagged_count(client, project):
    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    adherence = next(f for f in fields if f["name"] == "Adherence")
    contribution = next(f for f in fields if f["name"] == "Contribution Type")

    fully_tagged = client.post(
        f"/api/projects/{project['id']}/papers", json={"title": "Full"}
    ).json()["paper"]
    partially_tagged = client.post(
        f"/api/projects/{project['id']}/papers", json={"title": "Partial"}
    ).json()["paper"]

    client.post(
        f"/api/projects/{project['id']}/papers/{fully_tagged['id']}/tags/{adherence['options'][0]['id']}"
    )
    client.post(
        f"/api/projects/{project['id']}/papers/{fully_tagged['id']}/tags/{contribution['options'][0]['id']}"
    )
    client.post(
        f"/api/projects/{project['id']}/papers/{partially_tagged['id']}/tags/{adherence['options'][0]['id']}"
    )

    body = client.get(f"/api/projects/{project['id']}/dashboard").json()
    assert body["fully_tagged_count"] == 1


def test_dashboard_with_notes_count(client, project):
    with_notes = client.post(f"/api/projects/{project['id']}/papers", json={"title": "A"}).json()[
        "paper"
    ]
    # Created but never given notes, so it must not be counted.
    client.post(f"/api/projects/{project['id']}/papers", json={"title": "B"})
    blank_notes = client.post(f"/api/projects/{project['id']}/papers", json={"title": "C"}).json()[
        "paper"
    ]

    client.patch(
        f"/api/projects/{project['id']}/papers/{with_notes['id']}", json={"notes": "Interesting"}
    )
    client.patch(f"/api/projects/{project['id']}/papers/{blank_notes['id']}", json={"notes": "   "})

    body = client.get(f"/api/projects/{project['id']}/dashboard").json()
    assert body["with_notes_count"] == 1


def test_dashboard_reports_the_scales_the_averages_are_read_against(client, project):
    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    adherence = next(f for f in fields if f["name"] == "Adherence")
    sufficient = next(o for o in adherence["options"] if o["value"] == "Sufficient")
    client.patch(
        f"/api/projects/{project['id']}/fields/{adherence['id']}/options/{sufficient['id']}",
        json={"weight": 2},
    )

    # An empty project has no best paper to compare against.
    empty = client.get(f"/api/projects/{project['id']}/dashboard").json()
    assert empty["max_rating"] == 5
    assert empty["max_score"] == 0

    low = client.post(f"/api/projects/{project['id']}/papers", json={"title": "Low"}).json()[
        "paper"
    ]
    high = client.post(f"/api/projects/{project['id']}/papers", json={"title": "High"}).json()[
        "paper"
    ]
    client.put(f"/api/projects/{project['id']}/papers/{low['id']}/rating", json={"rating": 1})
    client.put(f"/api/projects/{project['id']}/papers/{high['id']}/rating", json={"rating": 4})
    client.post(
        f"/api/projects/{project['id']}/papers/{high['id']}/tags/{sufficient['id']}",
    )

    body = client.get(f"/api/projects/{project['id']}/dashboard").json()
    assert body["max_rating"] == 5
    # High: rating 4 + a tag weighted 2. Low: rating 1, no tags.
    assert body["max_score"] == 6
    assert body["average_score"] == 3.5
