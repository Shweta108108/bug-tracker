from tests.factories import add_member, auth_headers, create_issue, create_project, create_user


def _setup_project_with_member(db_session):
    maintainer = create_user(db_session)
    member = create_user(db_session, email="member@example.com")
    project = create_project(db_session, owner=maintainer, key="ISS1")
    add_member(db_session, project=project, user=member)
    return maintainer, member, project


def test_member_creates_issue_as_reporter(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    resp = client.post(
        f"/api/projects/{project.id}/issues",
        json={"title": "Bug 1", "description": "desc", "priority": "high"},
        headers=auth_headers(member),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["reporter"]["email"] == "member@example.com"
    assert body["status"] == "open"


def test_non_member_cannot_create_issue(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    outsider = create_user(db_session, email="outsider@example.com")
    resp = client.post(
        f"/api/projects/{project.id}/issues",
        json={"title": "Bug", "priority": "low"},
        headers=auth_headers(outsider),
    )
    assert resp.status_code == 403


def test_reporter_edits_own_title_and_description(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)

    resp = client.patch(
        f"/api/issues/{issue.id}",
        json={"title": "Updated title", "description": "Updated desc"},
        headers=auth_headers(member),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated title"


def test_reporter_cannot_change_status_or_assignee(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)

    resp = client.patch(
        f"/api/issues/{issue.id}", json={"status": "resolved"}, headers=auth_headers(member)
    )
    assert resp.status_code == 403

    resp2 = client.patch(
        f"/api/issues/{issue.id}",
        json={"assignee_id": maintainer.id},
        headers=auth_headers(member),
    )
    assert resp2.status_code == 403


def test_non_reporter_member_cannot_edit_issue(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    other_member = create_user(db_session, email="other@example.com")
    add_member(db_session, project=project, user=other_member)
    issue = create_issue(db_session, project=project, reporter=member)

    resp = client.patch(
        f"/api/issues/{issue.id}", json={"title": "Hijacked"}, headers=auth_headers(other_member)
    )
    assert resp.status_code == 403


def test_maintainer_can_edit_any_field_on_any_issue(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)

    resp = client.patch(
        f"/api/issues/{issue.id}",
        json={"status": "in_progress", "assignee_id": maintainer.id},
        headers=auth_headers(maintainer),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "in_progress"
    assert body["assignee"]["id"] == maintainer.id


def test_assignee_must_be_project_member(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)
    outsider = create_user(db_session, email="notmember@example.com")

    resp = client.patch(
        f"/api/issues/{issue.id}", json={"assignee_id": outsider.id}, headers=auth_headers(maintainer)
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "ASSIGNEE_NOT_MEMBER"


def test_maintainer_deletes_issue(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)

    resp = client.delete(f"/api/issues/{issue.id}", headers=auth_headers(maintainer))
    assert resp.status_code == 204

    get_resp = client.get(f"/api/issues/{issue.id}", headers=auth_headers(maintainer))
    assert get_resp.status_code == 404


def test_member_cannot_delete_issue(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)

    resp = client.delete(f"/api/issues/{issue.id}", headers=auth_headers(member))
    assert resp.status_code == 403


def test_filter_by_status(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    create_issue(db_session, project=project, reporter=member, status="open")
    create_issue(db_session, project=project, reporter=member, status="closed")

    resp = client.get(
        f"/api/projects/{project.id}/issues?status=closed", headers=auth_headers(member)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert all(i["status"] == "closed" for i in body["items"])


def test_filter_by_priority(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    create_issue(db_session, project=project, reporter=member, priority="critical")
    create_issue(db_session, project=project, reporter=member, priority="low")

    resp = client.get(
        f"/api/projects/{project.id}/issues?priority=critical", headers=auth_headers(member)
    )
    assert resp.json()["total"] == 1


def test_filter_by_assignee(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    create_issue(db_session, project=project, reporter=member, assignee=maintainer)
    create_issue(db_session, project=project, reporter=member)

    resp = client.get(
        f"/api/projects/{project.id}/issues?assignee_id={maintainer.id}", headers=auth_headers(member)
    )
    assert resp.json()["total"] == 1


def test_text_search_matches_title_case_insensitively(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    create_issue(db_session, project=project, reporter=member, title="Login button broken")
    create_issue(db_session, project=project, reporter=member, title="Unrelated issue")

    resp = client.get(f"/api/projects/{project.id}/issues?q=LOGIN", headers=auth_headers(member))
    body = resp.json()
    assert body["total"] == 1
    assert "Login" in body["items"][0]["title"]


def test_sort_by_priority_uses_severity_not_alphabetical(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    create_issue(db_session, project=project, reporter=member, title="low one", priority="low")
    create_issue(db_session, project=project, reporter=member, title="critical one", priority="critical")
    create_issue(db_session, project=project, reporter=member, title="medium one", priority="medium")

    resp = client.get(
        f"/api/projects/{project.id}/issues?sort=-priority", headers=auth_headers(member)
    )
    titles = [i["title"] for i in resp.json()["items"]]
    assert titles == ["critical one", "medium one", "low one"]


def test_sort_by_created_at_ascending(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    first = create_issue(db_session, project=project, reporter=member, title="first")
    second = create_issue(db_session, project=project, reporter=member, title="second")

    resp = client.get(
        f"/api/projects/{project.id}/issues?sort=created_at", headers=auth_headers(member)
    )
    titles = [i["title"] for i in resp.json()["items"]]
    assert titles == ["first", "second"]


def test_pagination(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    for i in range(5):
        create_issue(db_session, project=project, reporter=member, title=f"issue {i}")

    resp = client.get(
        f"/api/projects/{project.id}/issues?page=1&page_size=2&sort=created_at",
        headers=auth_headers(member),
    )
    body = resp.json()
    assert body["total"] == 5
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert len(body["items"]) == 2

    resp2 = client.get(
        f"/api/projects/{project.id}/issues?page=2&page_size=2&sort=created_at",
        headers=auth_headers(member),
    )
    body2 = resp2.json()
    assert len(body2["items"]) == 2
    assert body["items"][0]["id"] != body2["items"][0]["id"]


def test_combined_filter_search_sort(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    create_issue(db_session, project=project, reporter=member, title="Login crash", status="open", priority="high")
    create_issue(db_session, project=project, reporter=member, title="Login typo", status="closed", priority="low")
    create_issue(db_session, project=project, reporter=member, title="Other bug", status="open", priority="critical")

    resp = client.get(
        f"/api/projects/{project.id}/issues?q=login&status=open&sort=-priority",
        headers=auth_headers(member),
    )
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Login crash"


def test_list_issues_non_member_forbidden(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    outsider = create_user(db_session, email="notallowed@example.com")

    resp = client.get(f"/api/projects/{project.id}/issues", headers=auth_headers(outsider))
    assert resp.status_code == 403
