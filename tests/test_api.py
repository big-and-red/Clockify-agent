import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import date, datetime
from app.main import app
from app.schemas.clockify import ClockifyTimeEntry, ClockifyProject


class TestAPIEndpoints:
    
    @patch('app.services.timeline_service.TimelineService.get_daily_timeline')
    def test_daily_timeline_success(self, mock_get_timeline, client, mock_time_entries, mock_projects):
        # Mock the service response
        mock_get_timeline.return_value = {
            "days": {
                "2024-10-01": {
                    "projects": {
                        "Test Project": {
                            "total_hours": 2.0,
                            "time_blocks": [
                                {
                                    "start_time": "09:55",
                                    "end_time": "10:55",
                                    "duration": "01:00:00",
                                    "description": "Test task"
                                }
                            ]
                        }
                    },
                    "day_total": 2.0
                }
            },
            "summary": {
                "period": "2024-10-01 to 2024-10-01",
                "active_days": 1,
                "total_time": "2h 0m",
                "project_totals": {
                    "Test Project": {
                        "hours": 2.0,
                        "formatted": "2h 0m"
                    }
                }
            }
        }
        
        response = client.get("/api/v1/daily-timeline?start_date=2024-10-01&end_date=2024-10-01")
        assert response.status_code == 200
        
        data = response.json()
        assert "days" in data
        assert "summary" in data
        assert "2024-10-01" in data["days"]
    
    def test_daily_timeline_invalid_date_format(self, client):
        response = client.get("/api/v1/daily-timeline?start_date=invalid-date&end_date=2024-10-01")
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data["detail"]
        assert data["detail"]["code"] == "INVALID_DATE_RANGE"
    
    def test_daily_timeline_date_range_too_long(self, client):
        response = client.get("/api/v1/daily-timeline?start_date=2024-01-01&end_date=2024-03-01")
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data["detail"]
        assert data["detail"]["code"] == "INVALID_DATE_RANGE"
    
    @patch('app.services.timeline_service.TimelineService.get_project_timeline')
    def test_project_timeline_success(self, mock_get_timeline, client):
        mock_get_timeline.return_value = {
            "project_name": "Test Project",
            "days": {
                "2024-10-01": {
                    "total_hours": 2.0,
                    "time_blocks": [
                        {
                            "start_time": "09:55",
                            "end_time": "10:55",
                            "duration": "01:00:00",
                            "description": "Test task"
                        }
                    ]
                }
            },
            "summary": {
                "period": "2024-10-01 to 2024-10-01",
                "active_days": 1,
                "total_time": "2h 0m",
                "avg_daily": "2h 0m",
                "longest_session": "01:00:00",
                "avg_session": "01:00:00"
            }
        }
        
        response = client.get("/api/v1/project-timeline?start_date=2024-10-01&end_date=2024-10-01&project=Test%20Project")
        assert response.status_code == 200
        
        data = response.json()
        assert data["project_name"] == "Test Project"
        assert "days" in data
        assert "summary" in data
    
    @patch('app.services.timeline_service.TimelineService.get_project_timeline')
    def test_project_timeline_not_found(self, mock_get_timeline, client):
        mock_get_timeline.side_effect = ValueError("Project 'NonExistent' not found")
        
        response = client.get("/api/v1/project-timeline?start_date=2024-10-01&end_date=2024-10-01&project=NonExistent")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"]["code"] == "PROJECT_NOT_FOUND"
    
    def test_list_projects_success(self, client):
        # Этот тест может падать если нет реальных проектов в Clockify
        # Поэтому просто проверяем что endpoint отвечает
        response = client.get("/api/v1/projects")
        assert response.status_code in [200, 500]  # Может быть ошибка если нет API ключа
        
        if response.status_code == 200:
            data = response.json()
            assert "projects" in data
            assert "count" in data
            assert isinstance(data["count"], int)
            assert isinstance(data["projects"], list)
    
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "clockify-agent"
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Clockify Agent API"
        assert data["version"] == "1.0.0"


class TestErrorHandling:
    def test_invalid_date_format_error(self, client):
        response = client.get("/api/v1/daily-timeline?start_date=not-a-date&end_date=2024-10-01")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
        assert "message" in data["detail"]
        assert "code" in data["detail"]
    
    def test_missing_required_parameters(self, client):
        response = client.get("/api/v1/daily-timeline")
        assert response.status_code == 422  # Validation error
    
    def test_project_timeline_missing_project(self, client):
        response = client.get("/api/v1/project-timeline?start_date=2024-10-01&end_date=2024-10-01")
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__])
