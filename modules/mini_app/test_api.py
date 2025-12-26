import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "YouTube Income Commander" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_money_ideas():
    response = client.get("/money-ideas?count=3")
    assert response.status_code == 200
    data = response.json()
    assert "ideas" in data
    assert len(data["ideas"]) == 3
    assert "total_revenue_potential" in data
    assert data["total_revenue_potential"] > 0

def test_quick_strategy():
    response = client.get("/quick-strategy")
    assert response.status_code == 200
    data = response.json()
    assert "immediate_actions" in data
    assert "priority_content" in data
    assert "revenue_timeline" in data

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "app_name" in response.json()