from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

from app.main import app  # noqa: E402

client = TestClient(app)


def test_v4_dashboard_requires_authentication():
    response = client.get("/dashboard")
    assert response.status_code in (401, 403, 404)


def test_v4_metrics_requires_authentication():
    response = client.get("/metrics/business")
    assert response.status_code in (401, 403, 404)


def test_v4_me_route_not_exposed_without_auth():
    response = client.get("/me")
    assert response.status_code in (401, 403, 404)


def test_v4_audit_logs_protected_without_token():
    response = client.get("/audit-logs")
    assert response.status_code in (401, 403)


def test_v4_access_grants_protected_without_token():
    response = client.get("/access-grants")
    assert response.status_code in (401, 403)


def test_v4_non_regression_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_v4_non_regression_resources():
    response = client.get("/resources")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
