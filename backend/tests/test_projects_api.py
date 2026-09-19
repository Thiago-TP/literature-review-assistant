def test_new_review_has_an_empty_plan(client, project):
    resp = client.get(f"/api/projects/{project['id']}/plan")
    assert resp.status_code == 200
    plan = resp.json()

    assert plan["project_id"] == project["id"]
    assert plan["project_name"] == project["name"]
    assert all(
        plan[section] is None for section in ("purpose", "scope", "search", "weights", "other")
    )
    # Five sections + the two built-in fields + Adherence's three tags.
    assert plan["filled"] == 0
    assert plan["total"] == 10


def test_plan_read_carries_the_fields_and_their_tags(client, project):
    plan = client.get(f"/api/projects/{project['id']}/plan").json()
    names = [f["name"] for f in plan["fields"]]
    assert names == ["Adherence", "Contribution Type"]

    adherence = next(f for f in plan["fields"] if f["name"] == "Adherence")
    assert [o["value"] for o in adherence["options"]] == ["Insufficient", "Partial", "Sufficient"]
    assert all(o["description"] is None for o in adherence["options"])


def test_plan_sections_round_trip(client, project):
    resp = client.patch(
        f"/api/projects/{project['id']}/plan",
        json={"purpose": "Compare scheduling heuristics.", "search": "Scopus, 2026-09-19"},
    )
    assert resp.status_code == 200
    plan = resp.json()
    assert plan["purpose"] == "Compare scheduling heuristics."
    assert plan["search"] == "Scopus, 2026-09-19"
    assert plan["filled"] == 2

    assert client.get(f"/api/projects/{project['id']}/plan").json()["purpose"] == (
        "Compare scheduling heuristics."
    )


def test_patching_one_section_leaves_the_others_alone(client, project):
    client.patch(f"/api/projects/{project['id']}/plan", json={"purpose": "first"})
    client.patch(f"/api/projects/{project['id']}/plan", json={"scope": "second"})

    plan = client.get(f"/api/projects/{project['id']}/plan").json()
    assert plan["purpose"] == "first"
    assert plan["scope"] == "second"


def test_blank_section_reads_back_as_unwritten(client, project):
    """Whitespace is stored as null, so "written" has one meaning everywhere."""
    client.patch(f"/api/projects/{project['id']}/plan", json={"purpose": "   "})
    plan = client.get(f"/api/projects/{project['id']}/plan").json()
    assert plan["purpose"] is None
    assert plan["filled"] == 0


def test_describing_fields_and_adherence_completes_the_plan(client, project):
    project_id = project["id"]
    for section in ("purpose", "scope", "search", "weights", "other"):
        client.patch(f"/api/projects/{project_id}/plan", json={section: f"{section} text"})

    plan = client.get(f"/api/projects/{project_id}/plan").json()
    assert plan["filled"] == 5

    for field in plan["fields"]:
        client.patch(
            f"/api/projects/{project_id}/fields/{field['id']}",
            json={"description": f"what {field['name']} asks"},
        )

    adherence = next(f for f in plan["fields"] if f["name"] == "Adherence")
    for option in adherence["options"]:
        client.patch(
            f"/api/projects/{project_id}/fields/{adherence['id']}/options/{option['id']}",
            json={"description": f"{option['value']} means..."},
        )

    done = client.get(f"/api/projects/{project_id}/plan").json()
    assert done["filled"] == done["total"] == 10


def test_project_read_exposes_plan_progress(client, project):
    listed = client.get("/api/projects").json()[0]
    assert listed["plan_filled"] == 0
    assert listed["plan_total"] == 10

    client.patch(f"/api/projects/{project['id']}/plan", json={"purpose": "why"})

    single = client.get(f"/api/projects/{project['id']}").json()
    assert single["plan_filled"] == 1
    assert single["plan_total"] == 10


def test_a_custom_field_raises_the_plan_total(client, project):
    client.post(f"/api/projects/{project['id']}/fields", json={"name": "Domain"})
    plan = client.get(f"/api/projects/{project['id']}/plan").json()
    assert plan["total"] == 11


def test_plan_write_bumps_updated_at(client, project):
    before = client.get(f"/api/projects/{project['id']}").json()["updated_at"]
    client.patch(f"/api/projects/{project['id']}/plan", json={"purpose": "why"})
    after = client.get(f"/api/projects/{project['id']}").json()["updated_at"]
    assert after >= before


def test_plan_of_a_missing_project_is_404(client):
    assert client.get("/api/projects/9999/plan").status_code == 404
    assert client.patch("/api/projects/9999/plan", json={"purpose": "x"}).status_code == 404
