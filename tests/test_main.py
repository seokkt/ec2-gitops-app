from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "ec2-gitops-demo"
    assert data["status"] == "running"


def test_hello():
    response = client.get("/api/hello")

    assert response.status_code == 200
    assert response.json() == {
        "message": "hello from EC2 GitOps project"
    }


def test_health():
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_ready():
    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {
        "ready": True
    }


def test_version():
    response = client.get("/version")

    assert response.status_code == 200
    assert "version" in response.json()


def test_metrics():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text