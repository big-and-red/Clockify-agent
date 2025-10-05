import httpx
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import structlog
from app.core.config import settings
from app.schemas.clockify import ClockifyTimeEntry, ClockifyProject
from app.utils.validators import validate_api_key, validate_workspace_id, validate_user_id

logger = structlog.get_logger()

class ClockifyClient:
    def __init__(self):
        self.api_key = settings.clockify_api_key
        self.workspace_id = settings.clockify_workspace_id
        self.user_id = settings.clockify_user_id
        self.base_url = "https://api.clockify.me/api/v1"
        self.timeout = 30.0
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Валидирует конфигурацию клиента"""
        is_valid, error = validate_api_key(self.api_key)
        if not is_valid:
            raise ValueError(f"Invalid API key: {error}")
        
        is_valid, error = validate_workspace_id(self.workspace_id)
        if not is_valid:
            raise ValueError(f"Invalid workspace ID: {error}")
        
        is_valid, error = validate_user_id(self.user_id)
        if not is_valid:
            raise ValueError(f"Invalid user ID: {error}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Возвращает заголовки для запросов к Clockify API"""
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполняет HTTP запрос к Clockify API с обработкой ошибок"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **kwargs
                )
                
                if response.status_code == 401:
                    logger.error("Unauthorized request to Clockify API", status_code=401)
                    raise ValueError("Invalid API key or insufficient permissions")
                
                if response.status_code == 429:
                    logger.warning("Rate limit exceeded", status_code=429)
                    raise ValueError("Rate limit exceeded. Please try again later")
                
                if response.status_code >= 500:
                    logger.error("Clockify API server error", status_code=response.status_code)
                    raise ValueError("Clockify API is currently unavailable")
                
                response.raise_for_status()
                return response.json()
                
            except httpx.TimeoutException:
                logger.error("Request timeout", url=url)
                raise ValueError("Request timeout. Please try again later")
            except httpx.RequestError as e:
                logger.error("Request error", url=url, error=str(e))
                raise ValueError("Failed to connect to Clockify API")
    
    async def get_time_entries(self, start_date: date, end_date: date) -> List[ClockifyTimeEntry]:
        """Получает временные записи за указанный период"""
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        endpoint = f"/workspaces/{self.workspace_id}/user/{self.user_id}/time-entries"
        params = {
            "start": f"{start_str}T00:00:00Z",
            "end": f"{end_str}T23:59:59Z"
        }
        
        logger.info("Fetching time entries", start_date=start_str, end_date=end_str)
        
        try:
            data = await self._make_request("GET", endpoint, params=params)
            entries = [ClockifyTimeEntry(**entry) for entry in data]
            
            logger.info("Successfully fetched time entries", count=len(entries))
            return entries
            
        except Exception as e:
            logger.error("Failed to fetch time entries", error=str(e))
            raise
    
    async def get_projects(self) -> List[ClockifyProject]:
        """Получает список всех активных проектов в рабочем пространстве"""
        endpoint = f"/workspaces/{self.workspace_id}/projects"
        
        logger.info("Fetching projects")
        
        try:
            data = await self._make_request("GET", endpoint)
            # Фильтруем только активные проекты (не архивированные)
            active_projects = [ClockifyProject(**project) for project in data if not project.get("archived", False)]
            
            logger.info("Successfully fetched projects", total=len(data), active=len(active_projects))
            return active_projects
            
        except Exception as e:
            logger.error("Failed to fetch projects", error=str(e))
            raise
    
    async def get_project_by_name(self, project_name: str) -> Optional[ClockifyProject]:
        """Находит проект по точному названию"""
        projects = await self.get_projects()
        
        for project in projects:
            if project.name == project_name:
                return project
        
        return None
    
    async def test_connection(self) -> bool:
        """Тестирует соединение с Clockify API"""
        try:
            endpoint = f"/workspaces/{self.workspace_id}"
            await self._make_request("GET", endpoint)
            return True
        except Exception as e:
            logger.error("Connection test failed", error=str(e))
            return False
