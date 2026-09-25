from tests.conftest import SAMPLE_CSV_PATH, SAMPLE_XLSX_PATH

XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _upload_sample(client, project_id, path=SAMPLE_XLSX_PATH, content_type=XLSX_TYPE):
    with path.open("rb") as f:
        return client.post(
            f"/api/projects/{project_id}/import/preview",
            files={"file": (path.name, f, content_type)},
        )


def _upload_sample_csv(client, project_id):
    return _upload_sample(client, project_id, SAMPLE_CSV_PATH, "text/csv")


def _commit_all(client, project_id, preview):
    actions = {row["row_index"]: "add" for row in preview["rows"]}
    return client.post(
        f"/api/projects/{project_id}/import/commit",
        json={"rows": preview["rows"], "actions": actions},
    )


def test_preview_sample_file_all_new(client, project):
    resp = _upload_sample(client, project["id"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["new_count"] == 5
    assert body["duplicate_count"] == 0


def test_preview_sample_csv_all_new(client, project):
    resp = _upload_sample_csv(client, project["id"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["new_count"] == 5
    assert body["duplicate_count"] == 0


def test_commit_then_reimport_flags_all_as_duplicates(client, project):
    preview = _upload_sample(client, project["id"]).json()
    commit_resp = _commit_all(client, project["id"], preview)
    assert commit_resp.status_code == 200
    assert commit_resp.json()["added_count"] == 5

    papers = client.get(f"/api/projects/{project['id']}/papers").json()
    assert len(papers) == 5

    second_preview = _upload_sample(client, project["id"]).json()
    assert second_preview["new_count"] == 0
    assert second_preview["duplicate_count"] == 5


def test_csv_of_already_imported_xlsx_is_all_duplicates(client, project):
    # Exporting the same search twice, once in each format, must not double
    # the review.
    preview = _upload_sample(client, project["id"]).json()
    _commit_all(client, project["id"], preview)

    csv_preview = _upload_sample_csv(client, project["id"]).json()
    assert csv_preview["new_count"] == 0
    assert csv_preview["duplicate_count"] == 5


def test_commit_respects_skip_action(client, project):
    preview = _upload_sample(client, project["id"]).json()
    first_row = preview["rows"][0]
    actions = {row["row_index"]: "add" for row in preview["rows"]}
    actions[first_row["row_index"]] = "skip"

    commit_resp = client.post(
        f"/api/projects/{project['id']}/import/commit",
        json={"rows": preview["rows"], "actions": actions},
    )
    body = commit_resp.json()
    assert body["added_count"] == 4
    assert body["skipped_count"] == 1


def test_preview_rejects_bad_file(client, project):
    resp = client.post(
        f"/api/projects/{project['id']}/import/preview",
        files={"file": ("bad.xlsx", b"not an xlsx file", "application/octet-stream")},
    )
    assert resp.status_code == 400
