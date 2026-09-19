def test_project_creation_seeds_protected_fields(client, project):
    response = client.get(f"/api/projects/{project['id']}/fields")
    fields = response.json()
    names = {f["name"] for f in fields}
    assert names == {"Adherence", "Contribution Type"}
    assert all(f["is_protected"] for f in fields)


def test_create_paper_and_tag_it(client, project):
    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    adherence = next(f for f in fields if f["name"] == "Adherence")
    sufficient_option = next(o for o in adherence["options"] if o["value"] == "Sufficient")

    create_resp = client.post(
        f"/api/projects/{project['id']}/papers",
        json={"title": "My Paper", "abstract": "Abstract text", "doi": "10.1/xyz"},
    )
    assert create_resp.status_code == 201
    paper = create_resp.json()["paper"]

    patch_resp = client.patch(
        f"/api/projects/{project['id']}/papers/{paper['id']}",
        json={"notes": "Interesting paper", "tags": {adherence["id"]: [sufficient_option["id"]]}},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["notes"] == "Interesting paper"
    assert updated["tags"][str(adherence["id"])] == [sufficient_option["id"]]

    list_resp = client.get(f"/api/projects/{project['id']}/papers")
    item = list_resp.json()[0]
    assert item["filled_field_count"] == 1
    assert item["total_field_count"] == 2


def test_duplicate_paper_by_doi_is_rejected(client, project):
    client.post(
        f"/api/projects/{project['id']}/papers",
        json={"title": "Paper A", "doi": "10.1/same"},
    )
    dup_resp = client.post(
        f"/api/projects/{project['id']}/papers",
        json={"title": "Paper A but different title", "doi": "https://doi.org/10.1/SAME"},
    )
    assert dup_resp.status_code == 201
    body = dup_resp.json()
    assert body["paper"] is None
    assert body["duplicate"]["is_duplicate"]
    assert body["duplicate"]["reason"] == "doi"


def test_title_duplicate_without_doi_can_be_forced(client, project):
    """Two distinct papers can legitimately share a title (e.g. preprint vs.
    journal version) -- title-based duplicate detection must be overridable."""
    client.post(f"/api/projects/{project['id']}/papers", json={"title": "Shared Title"})
    forced_resp = client.post(
        f"/api/projects/{project['id']}/papers",
        json={"title": "Shared Title", "force": True},
    )
    assert forced_resp.status_code == 201
    assert forced_resp.json()["paper"] is not None


def test_doi_duplicate_cannot_be_forced(client, project):
    """Unlike title matches, a DOI collision is a real integrity constraint --
    forcing past it should fail loudly rather than create an inconsistent DB."""
    client.post(
        f"/api/projects/{project['id']}/papers", json={"title": "Paper B", "doi": "10.1/force"}
    )
    forced_resp = client.post(
        f"/api/projects/{project['id']}/papers",
        json={"title": "Paper B", "doi": "10.1/force", "force": True},
    )
    assert forced_resp.status_code == 409


def test_rename_field_preserves_tag_assignments(client, project):
    field_resp = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"})
    field = field_resp.json()
    option = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options", json={"value": "ML"}
    ).json()

    paper = client.post(
        f"/api/projects/{project['id']}/papers", json={"title": "Tagged Paper"}
    ).json()["paper"]
    client.patch(
        f"/api/projects/{project['id']}/papers/{paper['id']}",
        json={"tags": {field["id"]: [option["id"]]}},
    )

    rename_resp = client.patch(
        f"/api/projects/{project['id']}/fields/{field['id']}", json={"name": "Research Domain"}
    )
    assert rename_resp.status_code == 200

    paper_after = client.get(f"/api/projects/{project['id']}/papers/{paper['id']}").json()
    assert paper_after["tags"][str(field["id"])] == [option["id"]]


def test_cannot_delete_option_assigned_to_a_paper(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    option = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options", json={"value": "ML"}
    ).json()
    paper = client.post(
        f"/api/projects/{project['id']}/papers", json={"title": "Tagged Paper"}
    ).json()["paper"]
    client.patch(
        f"/api/projects/{project['id']}/papers/{paper['id']}",
        json={"tags": {field["id"]: [option["id"]]}},
    )

    delete_resp = client.delete(
        f"/api/projects/{project['id']}/fields/{field['id']}/options/{option['id']}"
    )
    assert delete_resp.status_code == 400
    assert paper["id"] in delete_resp.json()["detail"]["affected_paper_ids"]


def test_protected_field_cannot_be_renamed_or_deleted(client, project):
    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    protected = next(f for f in fields if f["is_protected"])

    rename_resp = client.patch(
        f"/api/projects/{project['id']}/fields/{protected['id']}", json={"name": "New Name"}
    )
    assert rename_resp.status_code == 400

    delete_resp = client.delete(f"/api/projects/{project['id']}/fields/{protected['id']}")
    assert delete_resp.status_code == 400


def test_last_viewed_paper_persists(client, project):
    paper = client.post(
        f"/api/projects/{project['id']}/papers", json={"title": "Resume Here"}
    ).json()["paper"]

    resp = client.patch(
        f"/api/projects/{project['id']}/last-viewed", json={"paper_id": paper["id"]}
    )
    assert resp.status_code == 200

    refetched = client.get(f"/api/projects/{project['id']}").json()
    assert refetched["last_viewed_paper_id"] == paper["id"]


def test_assign_tag_is_idempotent(client, project):
    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    adherence = next(f for f in fields if f["name"] == "Adherence")
    option = adherence["options"][0]
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]

    first = client.post(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{option['id']}")
    second = client.post(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{option['id']}")
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["tags"][str(adherence["id"])] == [option["id"]]


def test_unassign_tag_is_idempotent_when_not_assigned(client, project):
    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    option = fields[0]["options"][0]
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]

    resp = client.delete(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{option['id']}")
    assert resp.status_code == 200
    assert resp.json()["tags"] == {}


def test_assigning_two_different_tags_in_sequence_keeps_both(client, project):
    """Regression test: the old PATCH-with-full-list approach could drop an
    earlier selection if a second click's payload was computed from a
    slightly-stale snapshot. The per-option assign endpoint must never do
    that, since each call only ever asserts one option, never a full list."""
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

    client.post(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{topic['id']}")
    final = client.post(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{subtopic['id']}")

    assigned = set(final.json()["tags"][str(field["id"])])
    assert assigned == {topic["id"], subtopic["id"]}


def test_unassign_one_tag_leaves_other_selected(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    a = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options", json={"value": "A"}
    ).json()
    b = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options", json={"value": "B"}
    ).json()
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]

    client.post(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{a['id']}")
    client.post(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{b['id']}")
    final = client.delete(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{a['id']}")

    assert final.json()["tags"][str(field["id"])] == [b["id"]]


def test_new_paper_has_zero_score_and_no_rating(client, project):
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]
    assert paper["rating"] is None
    assert paper["score"] == 0


def test_set_and_clear_rating(client, project):
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]

    set_resp = client.put(
        f"/api/projects/{project['id']}/papers/{paper['id']}/rating", json={"rating": 4}
    )
    assert set_resp.status_code == 200
    assert set_resp.json()["rating"] == 4
    assert set_resp.json()["score"] == 4

    clear_resp = client.delete(f"/api/projects/{project['id']}/papers/{paper['id']}/rating")
    assert clear_resp.status_code == 200
    assert clear_resp.json()["rating"] is None
    assert clear_resp.json()["score"] == 0


def test_rating_out_of_range_rejected(client, project):
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]
    resp = client.put(
        f"/api/projects/{project['id']}/papers/{paper['id']}/rating", json={"rating": 5.5}
    )
    assert resp.status_code == 422
    resp = client.put(
        f"/api/projects/{project['id']}/papers/{paper['id']}/rating", json={"rating": 0}
    )
    assert resp.status_code == 422


def test_rating_must_be_a_half_step(client, project):
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]
    resp = client.put(
        f"/api/projects/{project['id']}/papers/{paper['id']}/rating", json={"rating": 3.3}
    )
    assert resp.status_code == 422


def test_half_star_rating_accepted(client, project):
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]
    resp = client.put(
        f"/api/projects/{project['id']}/papers/{paper['id']}/rating", json={"rating": 0.5}
    )
    assert resp.status_code == 200
    assert resp.json()["rating"] == 0.5

    resp = client.put(
        f"/api/projects/{project['id']}/papers/{paper['id']}/rating", json={"rating": 4.5}
    )
    assert resp.status_code == 200
    assert resp.json()["rating"] == 4.5
    assert resp.json()["score"] == 4.5


def test_score_combines_tag_weights_and_rating(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    option_a = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options",
        json={"value": "A", "weight": 3},
    ).json()
    option_b = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options",
        json={"value": "B", "weight": 1.5},
    ).json()
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]

    client.post(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{option_a['id']}")
    client.post(f"/api/projects/{project['id']}/papers/{paper['id']}/tags/{option_b['id']}")
    rated = client.put(
        f"/api/projects/{project['id']}/papers/{paper['id']}/rating", json={"rating": 5}
    )

    assert rated.json()["score"] == 3 + 1.5 + 5

    list_item = next(
        p
        for p in client.get(f"/api/projects/{project['id']}/papers").json()
        if p["id"] == paper["id"]
    )
    assert list_item["score"] == 3 + 1.5 + 5
    assert list_item["rating"] == 5


def test_paper_list_item_includes_notes(client, project):
    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "P"}).json()[
        "paper"
    ]
    client.patch(
        f"/api/projects/{project['id']}/papers/{paper['id']}", json={"notes": "Very relevant paper"}
    )

    list_item = next(
        p
        for p in client.get(f"/api/projects/{project['id']}/papers").json()
        if p["id"] == paper["id"]
    )
    assert list_item["notes"] == "Very relevant paper"
