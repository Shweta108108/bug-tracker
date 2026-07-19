from tests.factories import auth_headers, create_project, create_user


def test_create_project_makes_creator_maintainer(client, db_session):
    user = create_user(db_session)
    resp = client.post(
        "/api/projects",
        json={"name": "Test Project", "key": "TEST", "description": "desc"},
        headers=auth_headers(user),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "maintainer"
    assert body["key"] == "TEST"


def test_create_project_duplicate_key_conflict(client, db_session):
    user = create_user(db_session)
    create_project(db_session, owner=user, key="DUPE")
    resp = client.post(
        "/api/projects",
        json={"name": "Another", "key": "DUPE", "description": None},
        headers=auth_headers(user),
    )
    assert resp.status_code == 409


def test_list_projects_scoped_to_caller(client, db_session):
    alice = create_user(db_session)
    bob = create_user(db_session)
    create_project(db_session, owner=alice, key="ALICE1")
    create_project(db_session, owner=bob, key="BOB1")

    resp = client.get("/api/projects", headers=auth_headers(alice))
    assert resp.status_code == 200
    keys = {p["key"] for p in resp.json()}
    assert keys == {"ALICE1"}


def test_get_project_non_member_forbidden(client, db_session):
    alice = create_user(db_session)
    outsider = create_user(db_session)
    project = create_project(db_session, owner=alice, key="PRIV1")

    resp = client.get(f"/api/projects/{project.id}", headers=auth_headers(outsider))
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


def test_get_project_nonexistent_not_found(client, db_session):
    user = create_user(db_session)
    resp = client.get("/api/projects/999999", headers=auth_headers(user))
    assert resp.status_code == 404


def test_get_project_unauthenticated(client):
    resp = client.get("/api/projects")
    assert resp.status_code == 401
