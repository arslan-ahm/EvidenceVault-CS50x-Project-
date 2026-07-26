"""Tests for public endpoints: /api/public/stats, /api/public/reports,
/api/public/reports/{id}, /api/public/organizations."""

from uuid import uuid4

from app.core.security import hash_password
from app.db.session import engine
from app.models.case import Case
from app.models.organization import Organization
from app.models.user import User
from sqlmodel import Session


def _seed_data():
    """Helper to create base test data: a user, an org, and a public case."""
    with Session(engine) as session:
        org = Organization(
            id=str(uuid4()),
            name="TestCorp",
            slug="testcorp",
            description="A test organization",
            industry="Security",
        )
        user = User(
            id=str(uuid4()),
            email="pub-test@example.com",
            hashed_password=hash_password("StrongPass1!"),
            name="Public Tester",
        )
        case = Case(
            id=str(uuid4()),
            title="Public Report",
            description="A public vulnerability report",
            user_id=user.id,
            organization_id=org.id,
            category="web",
            severity="critical",
            status="open",
            is_public=True,
            views_count=42,
            upvotes_count=7,
        )
        session.add_all([org, user, case])
        session.commit()


class TestPublicStats:
    def test_stats_returns_counts(self, client):
        """GET /api/public/stats returns correct aggregate counts."""
        _seed_data()
        resp = client.get("/api/public/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_reports"] == 1
        assert data["total_organizations"] == 1
        assert data["active_researchers"] == 1
        assert data["resolved_reports"] == 0
        assert data["pending_reports"] == 1

    def test_stats_no_data(self, client):
        """With no data, zero counts are returned."""
        resp = client.get("/api/public/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_reports"] == 0
        assert data["total_organizations"] == 0
        assert data["active_researchers"] == 0

    def test_stats_public_only(self, client):
        """Non-public cases are excluded from stats."""
        # Create a non-public case
        with Session(engine) as session:
            user = User(
                id=str(uuid4()),
                email="private@example.com",
                hashed_password=hash_password("x"),
            )
            session.add(user)
            session.flush()
            private_case = Case(
                id=str(uuid4()),
                title="Private",
                user_id=user.id,
                is_public=False,
            )
            session.add(private_case)
            session.commit()

        resp = client.get("/api/public/stats")
        assert resp.status_code == 200
        assert resp.json()["total_reports"] == 0


class TestPublicReports:
    def test_list_reports(self, client):
        """GET /api/public/reports returns public reports."""
        _seed_data()
        resp = client.get("/api/public/reports")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Public Report"
        assert data[0]["organization_name"] == "TestCorp"

    def test_list_reports_empty(self, client):
        """With no public reports, an empty list is returned."""
        resp = client.get("/api/public/reports")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_reports_filter_category(self, client):
        """Query param ?category=web filters results."""
        _seed_data()
        resp = client.get("/api/public/reports?category=web")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        resp = client.get("/api/public/reports?category=network")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_reports_filter_severity(self, client):
        """Query param ?severity=critical filters results."""
        _seed_data()
        resp = client.get("/api/public/reports?severity=critical")
        assert len(resp.json()) == 1
        resp = client.get("/api/public/reports?severity=low")
        assert resp.json() == []

    def test_list_reports_pagination(self, client):
        """Query params ?limit=1&offset=0 work correctly."""
        with Session(engine) as session:
            user = User(id=str(uuid4()), email="many@example.com", hashed_password=hash_password("x"))
            session.add(user)
            session.flush()
            for i in range(3):
                session.add(Case(
                    id=str(uuid4()),
                    title=f"Report {i}",
                    user_id=user.id,
                    is_public=True,
                ))
            session.commit()

        resp = client.get("/api/public/reports?limit=2&offset=0")
        assert len(resp.json()) == 2

        resp = client.get("/api/public/reports?limit=2&offset=2")
        assert len(resp.json()) == 1

    def test_report_detail(self, client):
        """GET /api/public/reports/{id} returns full detail with evidence/timeline."""
        _seed_data()
        # Need to get the report ID
        resp = client.get("/api/public/reports")
        report_id = resp.json()[0]["id"]

        detail = client.get(f"/api/public/reports/{report_id}")
        assert detail.status_code == 200
        data = detail.json()
        assert data["report"]["title"] == "Public Report"
        assert data["report"]["organization_name"] == "TestCorp"
        assert "evidence" in data
        assert "timeline" in data

    def test_report_detail_not_found(self, client):
        """Non-existent report returns 404."""
        resp = client.get("/api/public/reports/nonexistent-id")
        assert resp.status_code == 404

    def test_report_detail_private_hidden(self, client):
        """Private reports return 404 on the public endpoint."""
        with Session(engine) as session:
            user = User(id=str(uuid4()), email="private2@example.com", hashed_password=hash_password("x"))
            session.add(user)
            session.flush()
            case = Case(id=str(uuid4()), title="Secret", user_id=user.id, is_public=False)
            session.add(case)
            session.commit()
            case_id = case.id

        resp = client.get(f"/api/public/reports/{case_id}")
        assert resp.status_code == 404


class TestPublicOrganizations:
    def test_list_organizations(self, client):
        """GET /api/public/organizations returns orgs with report counts."""
        _seed_data()
        resp = client.get("/api/public/organizations")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        org = next(o for o in data if o["slug"] == "testcorp")
        assert org["name"] == "TestCorp"
        assert org["total_reports"] == 1

    def test_list_organizations_empty(self, client):
        """With no orgs, an empty list is returned."""
        resp = client.get("/api/public/organizations")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_organizations_pagination(self, client):
        """Pagination works on organizations endpoint."""
        with Session(engine) as session:
            for i in range(3):
                session.add(Organization(
                    id=str(uuid4()),
                    name=f"Org {i}",
                    slug=f"org-{i}",
                ))
            session.commit()

        resp = client.get("/api/public/organizations?limit=2&offset=0")
        assert len(resp.json()) == 2

        resp = client.get("/api/public/organizations?limit=2&offset=2")
        assert len(resp.json()) == 1
