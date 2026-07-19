"""Populate the dev database with demo projects, users, issues, and comments.

Run from backend/ with the venv active: `python -m app.scripts.seed`
Safe to re-run — skips seeding if the demo maintainer account already exists.
"""

from app.dao import project_dao, user_dao
from app.db import SessionLocal
from app.services import auth_service, comment_service, issue_service, project_service

DEMO_PASSWORD = "password123"

DEMO_USERS = [
    ("Alice Maintainer", "alice@example.com"),
    ("Bob Developer", "bob@example.com"),
    ("Carol Developer", "carol@example.com"),
    ("Dave Reporter", "dave@example.com"),
]


def _get_or_create_user(db, name: str, email: str):
    existing = user_dao.get_by_email(db, email)
    if existing:
        return existing
    return auth_service.signup(db, name=name, email=email, password=DEMO_PASSWORD)


def seed() -> None:
    db = SessionLocal()
    try:
        if user_dao.get_by_email(db, "alice@example.com") is not None:
            print("Demo data already present (alice@example.com exists) - skipping seed.")
            return

        users = {name: _get_or_create_user(db, name, email) for name, email in DEMO_USERS}
        alice, bob, carol, dave = (users[name] for name, _ in DEMO_USERS)

        web = project_service.create_project(
            db, owner=alice, name="Website Revamp", key="WEB", description="Marketing site redesign"
        )
        project_service.add_member(db, project_id=web.id, requester=alice, email=bob.email, role="member")
        project_service.add_member(db, project_id=web.id, requester=alice, email=carol.email, role="member")

        mobile = project_service.create_project(
            db, owner=alice, name="Mobile App", key="MOB", description="iOS/Android client"
        )
        project_service.add_member(db, project_id=mobile.id, requester=alice, email=carol.email, role="maintainer")
        project_service.add_member(db, project_id=mobile.id, requester=alice, email=dave.email, role="member")

        web_issues_spec = [
            ("Homepage hero image broken on Safari", "open", "high", bob, alice),
            ("Contact form doesn't send confirmation email", "open", "critical", carol, None),
            ("Footer links point to old URLs", "in_progress", "low", bob, bob),
            ("Mobile nav menu overlaps logo", "in_progress", "medium", carol, alice),
            ("Blog pagination shows wrong page count", "open", "medium", bob, None),
            ("Newsletter signup validation too strict", "resolved", "low", carol, carol),
            ("Page load time regression after last deploy", "open", "critical", alice, bob),
            ("Favicon missing on new pages", "closed", "low", bob, bob),
            ("Search results not sorted by relevance", "open", "medium", carol, None),
            ("SSL certificate warning on staging", "resolved", "high", alice, alice),
        ]
        for title, status, priority, reporter, assignee in web_issues_spec:
            issue = issue_service.create_issue(
                db,
                project_id=web.id,
                reporter=reporter,
                title=title,
                description=f"Seed data: {title}",
                priority=priority,
                assignee_id=assignee.id if assignee else None,
            )
            if status != "open":
                alice_membership = project_dao.get_membership(db, project_id=web.id, user_id=alice.id)
                issue_service.update_issue(
                    db, issue=issue, user=alice, membership=alice_membership, patch={"status": status}
                )
            if title.startswith("Contact form"):
                comment_service.add_comment(db, issue_id=issue.id, author=bob, body="Can confirm, seeing this too.")
                comment_service.add_comment(
                    db, issue_id=issue.id, author=alice, body="Escalating to critical, investigating."
                )

        mobile_issues_spec = [
            ("App crashes on login for Android 12", "open", "critical", dave, carol),
            ("Push notifications delayed by several hours", "open", "high", dave, None),
            ("Dark mode toggle doesn't persist", "in_progress", "medium", carol, carol),
            ("Onboarding carousel skips last slide", "open", "low", dave, None),
            ("Biometric login fails on first attempt", "resolved", "high", carol, carol),
            ("App icon looks pixelated on iPad", "closed", "low", dave, dave),
        ]
        for title, status, priority, reporter, assignee in mobile_issues_spec:
            issue = issue_service.create_issue(
                db,
                project_id=mobile.id,
                reporter=reporter,
                title=title,
                description=f"Seed data: {title}",
                priority=priority,
                assignee_id=assignee.id if assignee else None,
            )
            if status != "open":
                carol_membership = project_dao.get_membership(db, project_id=mobile.id, user_id=carol.id)
                issue_service.update_issue(
                    db, issue=issue, user=carol, membership=carol_membership, patch={"status": status}
                )
            if title.startswith("App crashes"):
                comment_service.add_comment(
                    db, issue_id=issue.id, author=carol, body="Reproduced on Pixel 6, looking into it."
                )

        print("Seed complete. Demo accounts (all use password 'password123'):")
        for name, email in DEMO_USERS:
            print(f"  {email}  ({name})")
        print(f"Projects: {web.key} (Website Revamp), {mobile.key} (Mobile App)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
