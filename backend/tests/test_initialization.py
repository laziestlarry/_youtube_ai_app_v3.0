import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from ..main import app
from ..ai_modules.initialization_service import InitializationService
from ..ai_modules.management_engine import ManagementEngine
from ..ai_modules.content_strategy import ContentStrategyOptimizer
from ..ai_modules.analytics_engine import AnalyticsEngine
from ..ai_modules.content_optimizer import ContentOptimizer
from ..ai_modules.content_enhancer import ContentEnhancer

client = TestClient(app)

@pytest.fixture
def initialization_service():
    return InitializationService()

@pytest.fixture
def management_engine():
    return ManagementEngine()

@pytest.fixture
def strategy_optimizer():
    return ContentStrategyOptimizer()

@pytest.fixture
def analytics_engine():
    return AnalyticsEngine()

@pytest.fixture
def content_optimizer():
    return ContentOptimizer()

@pytest.fixture
def content_enhancer():
    return ContentEnhancer()

def test_initialization_start(initialization_service):
    """Test initialization process start."""
    response = client.post("/api/initialize")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "initialization_started"
    assert "message" in data

def test_initialization_status(initialization_service):
    """Test initialization status endpoint."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "progress" in data
    assert "current_task" in data
    assert "errors" in data

def test_analytics_initialization(initialization_service, analytics_engine):
    """Test analytics initialization."""
    analytics_config = {
        "tracking_frequency": "hourly",
        "metrics": ["views", "engagement", "revenue", "growth"],
        "alerts": {
            "threshold": 0.8,
            "notifications": ["email", "dashboard"]
        }
    }
    
    response = client.post("/api/configure-analytics", json=analytics_config)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "configuration" in data

def test_workflow_setup(initialization_service, management_engine):
    """Test workflow setup."""
    workflow_config = {
        "type": "content_generation",
        "config": {
            "schedule": "daily",
            "priority": "high",
            "resources": {
                "ai_models": ["gpt-4", "dall-e"],
                "processing_power": "high"
            }
        }
    }
    
    response = client.post("/api/setup-workflow", json=workflow_config)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == workflow_config["type"]
    assert data["status"] == "active"

def test_strategy_configuration(initialization_service, strategy_optimizer):
    """Test strategy configuration."""
    strategy_config = {
        "type": "content",
        "parameters": {
            "posting_frequency": "daily",
            "content_types": ["tutorial", "entertainment", "educational"],
            "optimization_targets": ["engagement", "views", "revenue"]
        }
    }
    
    response = client.post("/api/configure-strategy", json=strategy_config)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == strategy_config["type"]
    assert data["status"] == "active"

def test_content_calendar_initialization(initialization_service, strategy_optimizer):
    """Test content calendar initialization."""
    calendar_config = {
        "duration": "monthly",
        "content_types": ["tutorial", "entertainment", "educational"],
        "optimization_criteria": ["engagement", "views", "revenue"]
    }
    
    response = client.post("/api/manage-calendar", json={"content": calendar_config})
    assert response.status_code == 200
    data = response.json()
    assert "schedule" in data
    assert "optimization_suggestions" in data

def test_monitoring_setup(initialization_service, management_engine):
    """Test monitoring setup."""
    monitoring_config = {
        "monitoring": {
            "frequency": "real-time",
            "metrics": ["system_health", "performance", "resource_usage"],
            "alerts": {
                "threshold": 0.9,
                "notifications": ["email", "dashboard"]
            }
        }
    }
    
    response = client.post("/api/manage-operations", json=monitoring_config)
    assert response.status_code == 200
    data = response.json()
    assert "system_health" in data
    assert "performance_metrics" in data

def test_error_handling(initialization_service):
    """Test error handling during initialization."""
    # Test with invalid configuration
    invalid_config = {
        "type": "invalid_type",
        "config": {}
    }
    
    response = client.post("/api/setup-workflow", json=invalid_config)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data

def test_concurrent_initialization(initialization_service):
    """Test concurrent initialization requests."""
    # Start multiple initialization requests
    responses = []
    for _ in range(3):
        response = client.post("/api/initialize")
        responses.append(response)
    
    # Check that only one initialization is running
    statuses = [client.get("/api/status").json() for _ in range(3)]
    running_count = sum(1 for status in statuses if status["status"] == "initializing")
    assert running_count <= 1

def test_initialization_completion(initialization_service):
    """Test initialization completion and cleanup."""
    # Start initialization
    client.post("/api/initialize")
    
    # Wait for completion (mock the waiting)
    initialization_service.initialization_status["status"] = "completed"
    initialization_service.initialization_status["progress"] = 100
    
    # Check final status
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["progress"] == 100

def test_resource_cleanup(initialization_service):
    """Test resource cleanup after initialization."""
    # Start initialization
    client.post("/api/initialize")
    
    # Simulate completion
    initialization_service.initialization_status["status"] = "completed"
    
    # Check resource cleanup
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "errors" in data
    assert len(data["errors"]) == 0

def test_initialization_recovery(initialization_service):
    """Test initialization recovery after failure."""
    # Simulate failure
    initialization_service.initialization_status["status"] = "error"
    initialization_service.initialization_status["errors"] = ["Test error"]
    
    # Attempt recovery
    response = client.post("/api/initialize")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "initialization_started"
    
    # Check status after recovery attempt
    status_response = client.get("/api/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["status"] in ["initializing", "completed"] 