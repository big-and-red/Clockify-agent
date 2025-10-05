from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, date
from typing import Optional
import structlog

from app.services.timeline_service import TimelineService
from app.schemas.response import DailyTimelineResponse, ProjectTimelineResponse
from app.schemas.request import ErrorResponse
from app.utils.validators import validate_date_range
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()

def get_timeline_service() -> TimelineService:
    """Dependency для получения сервиса временной шкалы"""
    return TimelineService()

@router.get(
    "/daily-timeline",
    response_model=DailyTimelineResponse,
    summary="Get daily timeline",
    description="Get timeline data grouped by days and projects for a specified date range"
)
async def get_daily_timeline(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    timeline_service: TimelineService = Depends(get_timeline_service)
):
    """
    Получает ежедневную временную шкалу за указанный период.
    
    - **start_date**: Начальная дата в формате YYYY-MM-DD
    - **end_date**: Конечная дата в формате YYYY-MM-DD
    - **max_period**: Максимальный период 31 день
    
    Возвращает данные, сгруппированные по дням и проектам с временными блоками.
    """
    try:
        # Валидация дат
        is_valid, error_msg = validate_date_range(start_date, end_date, settings.max_period_days)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid date range",
                    "message": error_msg,
                    "code": "INVALID_DATE_RANGE"
                }
            )
        
        # Парсинг дат
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        logger.info("Processing daily timeline request", 
                   start_date=start_date, end_date=end_date)
        
        # Получение данных
        result = await timeline_service.get_daily_timeline(start, end)
        
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error("Validation error in daily timeline", error=str(e))
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid input",
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )
    except Exception as e:
        logger.error("Unexpected error in daily timeline", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )

@router.get(
    "/project-timeline",
    response_model=ProjectTimelineResponse,
    summary="Get project timeline",
    description="Get timeline data for a specific project over a date range"
)
async def get_project_timeline(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    project: str = Query(..., description="Exact project name from Clockify"),
    timeline_service: TimelineService = Depends(get_timeline_service)
):
    """
    Получает временную шкалу для конкретного проекта за указанный период.
    
    - **start_date**: Начальная дата в формате YYYY-MM-DD
    - **end_date**: Конечная дата в формате YYYY-MM-DD
    - **project**: Точное название проекта из Clockify
    - **max_period**: Максимальный период 31 день
    
    Возвращает данные по проекту, сгруппированные по дням с временными блоками.
    """
    try:
        # Валидация дат
        is_valid, error_msg = validate_date_range(start_date, end_date, settings.max_period_days)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid date range",
                    "message": error_msg,
                    "code": "INVALID_DATE_RANGE"
                }
            )
        
        # Парсинг дат
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        logger.info("Processing project timeline request", 
                   start_date=start_date, end_date=end_date, project=project)
        
        # Получение данных
        result = await timeline_service.get_project_timeline(start, end, project)
        
        return result
        
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            logger.warning("Project not found", project=project)
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Project not found",
                    "message": error_msg,
                    "code": "PROJECT_NOT_FOUND"
                }
            )
        else:
            logger.error("Validation error in project timeline", error=error_msg)
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid input",
                    "message": error_msg,
                    "code": "VALIDATION_ERROR"
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in project timeline", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )

@router.get(
    "/projects",
    summary="List available projects",
    description="Get list of all available projects in the workspace"
)
async def list_projects(timeline_service: TimelineService = Depends(get_timeline_service)):
    """
    Получает список всех доступных проектов в рабочем пространстве.
    
    Полезно для получения точных названий проектов для использования в project-timeline endpoint.
    """
    try:
        projects = await timeline_service.clockify_client.get_projects()
        project_names = [project.name for project in projects]
        
        return {
            "projects": project_names,
            "count": len(project_names)
        }
        
    except Exception as e:
        logger.error("Error listing projects", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to fetch projects",
                "code": "INTERNAL_ERROR"
            }
        )
