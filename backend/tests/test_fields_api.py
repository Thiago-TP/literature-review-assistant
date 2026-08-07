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

    rename_resp = client.patch(
        f"/api/projects/{project['id']}/fields/{field['id']}/options/{option['id']}",
        json={"value": "Machine Learning"},
    )
    assert rename_resp.status_code == 200

    delete_resp = client.delete(
        f"/api/projects/{project['id']}/fields/{field['id']}/options/{option['id']}"
    )
    assert delete_resp.status_code == 204
