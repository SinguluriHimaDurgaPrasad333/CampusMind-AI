import pytest
from fastapi.testclient import TestClient
from app.main import app, seed_initial_knowledge_base
from app.database.session import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_app():
    init_db()
    seed_initial_knowledge_base()


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "service" in data


def test_chat_grounded_answer():
    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={"query": "What is the minimum attendance requirement to write semester exams?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "75%" in data["answer"] or "attendance" in data["answer"].lower()
        assert len(data["sources"]) > 0
        assert any("attendance" in s["document_name"].lower() for s in data["sources"])


def test_chat_unavailable_information():
    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={"query": "Can students fly helicopters on campus without a pilot license?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "couldn't find reliable information" in data["answer"].lower()
        assert data["unanswered"] is True


def test_documents_list():
    with TestClient(app) as client:
        response = client.get("/api/documents")
        assert response.status_code == 200
        docs = response.json()
        assert len(docs) >= 8


def test_analytics_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/analytics")
        assert response.status_code == 200
        data = response.json()
        assert data["total_documents"] >= 8
        assert "category_distribution" in data


def test_admin_login():
    with TestClient(app) as client:
        # Invalid password
        bad_res = client.post("/api/admin/login", json={"username": "admin", "password": "wrongpassword"})
        assert bad_res.status_code == 401

        # Valid default password
        good_res = client.post("/api/admin/login", json={"username": "admin", "password": "campusmind2025"})
        assert good_res.status_code == 200
        assert "access_token" in good_res.json()
