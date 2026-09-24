import pytest
from fastapi.testclient import TestClient

from bmw_analyst.api.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_metrics():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_ask_empty_question():
    response = client.post(
        "/ask",
        json={
            "question": "",
        },
    )

    assert response.status_code in {400, 422}


def test_ask_success(monkeypatch):
    from bmw_analyst.api import main

    def mock_ask(question):
        return {
            "question": question,
            "intent": "warranty_cost",
            "sql": (
                "SELECT MODEL, SUM(WARRANTY_COST) AS TOTAL_WARRANTY_COST "
                "FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY "
                "WHERE CITY = 'Chennai' "
                "GROUP BY MODEL "
                "ORDER BY TOTAL_WARRANTY_COST DESC "
                "LIMIT 1"
            ),
            "data": [
                {
                    "MODEL": "BMW i5",
                    "TOTAL_WARRANTY_COST": 1136000.0,
                }
            ],
            "answer": "BMW i5 has the highest warranty cost in Chennai.",
        }

    monkeypatch.setattr(
        main.agent,
        "ask",
        mock_ask,
    )

    response = client.post(
        "/ask",
        json={
            "question": "Which BMW model had the highest warranty cost in Chennai?",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["question"] == (
        "Which BMW model had the highest warranty cost in Chennai?"
    )
    assert body["intent"] == "warranty_cost"
    assert body["data"][0]["MODEL"] == "BMW i5"
    assert body["data"][0]["TOTAL_WARRANTY_COST"] == 1136000.0


def test_agent_value_error(monkeypatch):
    from bmw_analyst.api import main

    def mock_ask(question):
        raise ValueError("Generated SQL failed security validation.")

    monkeypatch.setattr(
        main.agent,
        "ask",
        mock_ask,
    )

    response = client.post(
        "/ask",
        json={
            "question": "Show warranty cost",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["answer"] == (
        "I can only answer questions related to BMW analytical data. "
        "You can ask about vehicle sales, warranty costs, faults, or battery status."
    )


def test_agent_internal_error(monkeypatch):
    from bmw_analyst.api import main

    def mock_ask(question):
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        main.agent,
        "ask",
        mock_ask,
    )

    response = client.post(
        "/ask",
        json={
            "question": "Show warranty cost",
        },
    )

    assert response.status_code == 500

    assert response.json()["detail"] == (
        "I couldn't process your request right now. Please try again."
    )


def test_request_id_header():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_openapi():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    body = response.json()

    assert body["info"]["title"] == "BMW Natural Language Data Analyst"
