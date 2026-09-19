def test_add_rename_delete_custom_field(client, project):
    create_resp = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"})
    assert create_resp.status_code == 201
    field = create_resp.json()
    assert field["is_protected"] is False

    rename_resp = client.patch(
        f"/api/projects/{project['id']}/fields/{field['id']}", json={"name": "Research Domain"}
    )
    assert rename_resp.status_code == 200
    assert rename_resp.json()["name"] == "Research Domain"

    delete_resp = client.delete(f"/api/projects/{project['id']}/fields/{field['id']}")
    assert delete_resp.status_code == 204

    fields_after = client.get(f"/api/projects/{project['id']}/fields").json()
    assert all(f["name"] != "Research Domain" for f in fields_after)


def test_duplicate_field_name_rejected(client, project):
    client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"})
    dup_resp = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"})
    assert dup_resp.status_code == 400


def test_add_rename_delete_unassigned_option(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()

    option_resp = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options", json={"value": "ML"}
    )
    assert option_resp.status_code == 201
    option = option_resp.json()
    assert option["children"] == []

    rename_resp = client.patch(
        f"/api/projects/{project['id']}/fields/{field['id']}/options/{option['id']}",
        json={"value": "Machine Learning"},
    )
    assert rename_resp.status_code == 200

    delete_resp = client.delete(
        f"/api/projects/{project['id']}/fields/{field['id']}/options/{option['id']}"
    )
    assert delete_resp.status_code == 204


def test_create_nested_subtopic_and_subsubtopic(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    fid = field["id"]

    topic = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options", json={"value": "Machine Learning"}
    ).json()
    subtopic = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options",
        json={"value": "Deep Learning", "parent_option_id": topic["id"]},
    ).json()
    assert subtopic["children"] == []
    subsubtopic = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options",
        json={"value": "Transformers", "parent_option_id": subtopic["id"]},
    )
    assert subsubtopic.status_code == 201

    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    domain = next(f for f in fields if f["id"] == fid)
    assert len(domain["options"]) == 1
    ml = domain["options"][0]
    assert ml["value"] == "Machine Learning"
    assert len(ml["children"]) == 1
    dl = ml["children"][0]
    assert dl["value"] == "Deep Learning"
    assert len(dl["children"]) == 1
    assert dl["children"][0]["value"] == "Transformers"


def test_same_value_allowed_under_different_parents(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    fid = field["id"]
    topic_a = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options", json={"value": "Topic A"}
    ).json()
    topic_b = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options", json={"value": "Topic B"}
    ).json()

    resp_a = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options",
        json={"value": "Shared Name", "parent_option_id": topic_a["id"]},
    )
    resp_b = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options",
        json={"value": "Shared Name", "parent_option_id": topic_b["id"]},
    )
    assert resp_a.status_code == 201
    assert resp_b.status_code == 201


def test_duplicate_value_rejected_under_same_parent(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    fid = field["id"]
    topic = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options", json={"value": "Topic"}
    ).json()
    client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options",
        json={"value": "Sub", "parent_option_id": topic["id"]},
    )
    dup_resp = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options",
        json={"value": "Sub", "parent_option_id": topic["id"]},
    )
    assert dup_resp.status_code == 400


def test_create_option_rejects_parent_from_different_field(client, project):
    field_a = client.post(f"/api/projects/{project['id']}/fields", json={"name": "A"}).json()
    field_b = client.post(f"/api/projects/{project['id']}/fields", json={"name": "B"}).json()
    topic = client.post(
        f"/api/projects/{project['id']}/fields/{field_a['id']}/options", json={"value": "Topic"}
    ).json()

    resp = client.post(
        f"/api/projects/{project['id']}/fields/{field_b['id']}/options",
        json={"value": "Sub", "parent_option_id": topic["id"]},
    )
    assert resp.status_code == 404


def test_cannot_delete_topic_when_subsubtopic_is_assigned(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    fid = field["id"]
    topic = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options", json={"value": "Topic"}
    ).json()
    subtopic = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options",
        json={"value": "Sub", "parent_option_id": topic["id"]},
    ).json()
    subsubtopic = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options",
        json={"value": "SubSub", "parent_option_id": subtopic["id"]},
    ).json()

    paper = client.post(f"/api/projects/{project['id']}/papers", json={"title": "Paper"}).json()[
        "paper"
    ]
    client.patch(
        f"/api/projects/{project['id']}/papers/{paper['id']}",
        json={"tags": {fid: [subsubtopic["id"]]}},
    )

    delete_resp = client.delete(f"/api/projects/{project['id']}/fields/{fid}/options/{topic['id']}")
    assert delete_resp.status_code == 400
    assert paper["id"] in delete_resp.json()["detail"]["affected_paper_ids"]


def test_delete_topic_cascades_to_unassigned_subtopics(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    fid = field["id"]
    topic = client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options", json={"value": "Topic"}
    ).json()
    client.post(
        f"/api/projects/{project['id']}/fields/{fid}/options",
        json={"value": "Sub", "parent_option_id": topic["id"]},
    )

    delete_resp = client.delete(f"/api/projects/{project['id']}/fields/{fid}/options/{topic['id']}")
    assert delete_resp.status_code == 204

    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    domain = next(f for f in fields if f["id"] == fid)
    assert domain["options"] == []


def test_option_defaults_to_zero_weight(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    option = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options", json={"value": "A"}
    ).json()
    assert option["weight"] == 0


def test_create_option_with_weight(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    option = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options",
        json={"value": "A", "weight": 2.5},
    ).json()
    assert option["weight"] == 2.5


def test_create_option_weight_above_cap_rejected(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    resp = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options",
        json={"value": "A", "weight": 5.5},
    )
    assert resp.status_code == 422


def test_create_option_weight_off_step_rejected(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    resp = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options",
        json={"value": "A", "weight": 2.3},
    )
    assert resp.status_code == 422


def test_create_option_weight_at_cap_accepted(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    resp = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options",
        json={"value": "A", "weight": 5},
    )
    assert resp.status_code == 201
    assert resp.json()["weight"] == 5


def test_reweight_option_above_cap_rejected(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    option = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options", json={"value": "A"}
    ).json()
    resp = client.patch(
        f"/api/projects/{project['id']}/fields/{field['id']}/options/{option['id']}",
        json={"weight": 10},
    )
    assert resp.status_code == 422


def test_reweight_option_without_changing_value(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    option = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options", json={"value": "A"}
    ).json()

    resp = client.patch(
        f"/api/projects/{project['id']}/fields/{field['id']}/options/{option['id']}",
        json={"weight": 4},
    )
    assert resp.status_code == 200
    assert resp.json()["value"] == "A"
    assert resp.json()["weight"] == 4


def test_protected_field_option_can_be_reweighted_but_not_renamed(client, project):
    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    protected = next(f for f in fields if f["is_protected"])
    option = protected["options"][0]

    reweight_resp = client.patch(
        f"/api/projects/{project['id']}/fields/{protected['id']}/options/{option['id']}",
        json={"weight": 3},
    )
    assert reweight_resp.status_code == 200
    assert reweight_resp.json()["weight"] == 3

    rename_resp = client.patch(
        f"/api/projects/{project['id']}/fields/{protected['id']}/options/{option['id']}",
        json={"value": "Something Else"},
    )
    assert rename_resp.status_code == 400


def test_protected_field_can_be_described_but_not_renamed(client, project):
    """Saying what Adherence asks of a paper is the point of the review plan,
    so a description must get through the same guard that blocks a rename."""
    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    protected = next(f for f in fields if f["is_protected"])

    describe_resp = client.patch(
        f"/api/projects/{project['id']}/fields/{protected['id']}",
        json={"description": "Does the paper actually address the research question?"},
    )
    assert describe_resp.status_code == 200
    assert describe_resp.json()["description"] == (
        "Does the paper actually address the research question?"
    )

    rename_resp = client.patch(
        f"/api/projects/{project['id']}/fields/{protected['id']}",
        json={"name": "Relevance"},
    )
    assert rename_resp.status_code == 400


def test_protected_option_can_be_described(client, project):
    fields = client.get(f"/api/projects/{project['id']}/fields").json()
    protected = next(f for f in fields if f["name"] == "Adherence")
    option = next(o for o in protected["options"] if o["value"] == "Sufficient")

    resp = client.patch(
        f"/api/projects/{project['id']}/fields/{protected['id']}/options/{option['id']}",
        json={"description": "Directly answers the question with its own data."},
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Directly answers the question with its own data."


def test_description_survives_a_reweight(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    option = client.post(
        f"/api/projects/{project['id']}/fields/{field['id']}/options",
        json={"value": "Robotics"},
    ).json()

    client.patch(
        f"/api/projects/{project['id']}/fields/{field['id']}/options/{option['id']}",
        json={"description": "Anything with an actuator in the loop."},
    )
    resp = client.patch(
        f"/api/projects/{project['id']}/fields/{field['id']}/options/{option['id']}",
        json={"weight": 2.5},
    )
    assert resp.status_code == 200
    assert resp.json()["weight"] == 2.5
    assert resp.json()["description"] == "Anything with an actuator in the loop."


def test_blank_description_clears_it(client, project):
    field = client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"}).json()
    client.patch(
        f"/api/projects/{project['id']}/fields/{field['id']}", json={"description": "something"}
    )
    resp = client.patch(
        f"/api/projects/{project['id']}/fields/{field['id']}", json={"description": "   "}
    )
    assert resp.json()["description"] is None
