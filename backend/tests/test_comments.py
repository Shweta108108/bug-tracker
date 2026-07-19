from tests.factories import add_member, auth_headers, create_comment, create_issue, create_project, create_user


def _setup_project_with_member(db_session):
    maintainer = create_user(db_session)
    member = create_user(db_session, email="member@example.com")
    project = create_project(db_session, owner=maintainer, key="COM1")
    add_member(db_session, project=project, user=member)
    return maintainer, member, project


def test_member_adds_comment(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)

    resp = client.post(
        f"/api/issues/{issue.id}/comments", json={"body": "Looks good to me"}, headers=auth_headers(member)
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["body"] == "Looks good to me"
    assert body["author"]["email"] == "member@example.com"


def test_maintainer_can_comment_on_issue_they_did_not_report(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)

    resp = client.post(
        f"/api/issues/{issue.id}/comments", json={"body": "Maintainer note"}, headers=auth_headers(maintainer)
    )
    assert resp.status_code == 201


def test_comments_returned_in_chronological_order(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)
    create_comment(db_session, issue=issue, author=member, body="first")
    create_comment(db_session, issue=issue, author=maintainer, body="second")

    resp = client.get(f"/api/issues/{issue.id}/comments", headers=auth_headers(member))
    assert resp.status_code == 200
    bodies = [c["body"] for c in resp.json()]
    assert bodies == ["first", "second"]


def test_non_member_cannot_read_comments(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)
    outsider = create_user(db_session, email="outsider@example.com")

    resp = client.get(f"/api/issues/{issue.id}/comments", headers=auth_headers(outsider))
    assert resp.status_code == 403


def test_non_member_cannot_add_comment(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)
    outsider = create_user(db_session, email="outsider2@example.com")

    resp = client.post(
        f"/api/issues/{issue.id}/comments", json={"body": "sneaky"}, headers=auth_headers(outsider)
    )
    assert resp.status_code == 403


def test_comment_on_nonexistent_issue_not_found(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    resp = client.post(
        "/api/issues/999999/comments", json={"body": "hello"}, headers=auth_headers(member)
    )
    assert resp.status_code == 404


def test_empty_comment_body_rejected(client, db_session):
    maintainer, member, project = _setup_project_with_member(db_session)
    issue = create_issue(db_session, project=project, reporter=member)

    resp = client.post(f"/api/issues/{issue.id}/comments", json={"body": ""}, headers=auth_headers(member))
    assert resp.status_code == 422
