from tests.factories import add_member, auth_headers, create_project, create_user


def test_maintainer_adds_existing_user(client, db_session):
    maintainer = create_user(db_session)
    new_member = create_user(db_session, email="newmember@example.com")
    project = create_project(db_session, owner=maintainer, key="ADD1")

    resp = client.post(
        f"/api/projects/{project.id}/members",
        json={"email": "newmember@example.com", "role": "member"},
        headers=auth_headers(maintainer),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "member"
    assert body["user"]["email"] == "newmember@example.com"

    list_resp = client.get(f"/api/projects/{project.id}/members", headers=auth_headers(maintainer))
    emails = {m["user"]["email"] for m in list_resp.json()}
    assert "newmember@example.com" in emails


def test_add_member_unknown_email_not_found(client, db_session):
    maintainer = create_user(db_session)
    project = create_project(db_session, owner=maintainer, key="ADD2")

    resp = client.post(
        f"/api/projects/{project.id}/members",
        json={"email": "ghost@example.com", "role": "member"},
        headers=auth_headers(maintainer),
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "USER_NOT_FOUND"


def test_add_member_duplicate_conflict(client, db_session):
    maintainer = create_user(db_session)
    existing = create_user(db_session, email="existing@example.com")
    project = create_project(db_session, owner=maintainer, key="ADD3")
    add_member(db_session, project=project, user=existing)

    resp = client.post(
        f"/api/projects/{project.id}/members",
        json={"email": "existing@example.com", "role": "member"},
        headers=auth_headers(maintainer),
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "ALREADY_MEMBER"


def test_non_maintainer_cannot_add_member(client, db_session):
    maintainer = create_user(db_session)
    regular_member = create_user(db_session, email="member@example.com")
    someone_else = create_user(db_session, email="someone@example.com")
    project = create_project(db_session, owner=maintainer, key="ADD4")
    add_member(db_session, project=project, user=regular_member)

    resp = client.post(
        f"/api/projects/{project.id}/members",
        json={"email": "someone@example.com", "role": "member"},
        headers=auth_headers(regular_member),
    )
    assert resp.status_code == 403


def test_add_member_unauthenticated(client, db_session):
    maintainer = create_user(db_session)
    project = create_project(db_session, owner=maintainer, key="ADD5")

    resp = client.post(
        f"/api/projects/{project.id}/members", json={"email": "x@example.com", "role": "member"}
    )
    assert resp.status_code == 401
