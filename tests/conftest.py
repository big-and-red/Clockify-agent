import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import date, datetime
from app.main import app
from app.schemas.clockify import ClockifyTimeEntry, ClockifyProject


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_time_entries():
    """Mock time entries for testing"""
    return [
        ClockifyTimeEntry(
            id="1",
            description="Test task",
            userId="user123",
            billable=True,
            projectId="project123",
            workspaceId="workspace123",
            timeInterval={
                "start": "2024-10-01T06:55:00Z",
                "end": "2024-10-01T07:55:00Z",
                "duration": "PT1H"
            },
            type="REGULAR",
            isLocked=False
        ),
        ClockifyTimeEntry(
            id="2",
            description="Another task",
            userId="user123",
            billable=True,
            projectId="project123",
            workspaceId="workspace123",
            timeInterval={
                "start": "2024-10-01T08:00:00Z",
                "end": "2024-10-01T09:00:00Z",
                "duration": "PT1H"
            },
            type="REGULAR",
            isLocked=False
        )
    ]


@pytest.fixture
def mock_projects():
    """Mock projects for testing"""
    return [
        ClockifyProject(
            id="project123",
            name="Test Project",
            workspaceId="workspace123",
            billable=True,
            color="#FF0000",
            archived=False,
            public=True,
            template=False
        )
    ]


@pytest.fixture
def mock_timeline_service():
    """Mock timeline service for testing"""
    service = AsyncMock()
    service.get_daily_timeline.return_value = {
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
    
    service.get_project_timeline.return_value = {
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
    
    return service
