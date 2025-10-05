from datetime import datetime, date
from typing import Tuple
import structlog

logger = structlog.get_logger()

def validate_date_range(start_date: str, end_date: str, max_days: int = 31) -> Tuple[bool, str]:
    """Валидирует диапазон дат"""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start > end:
            return False, "Start date must be before or equal to end date"
        
        if (end - start).days > max_days:
            return False, f"Date range cannot exceed {max_days} days"
        
        return True, ""
    except ValueError as e:
        return False, "Invalid date format. Use YYYY-MM-DD"

def validate_project_name(name: str) -> Tuple[bool, str]:
    """Валидирует название проекта"""
    if not name or not name.strip():
        return False, "Project name cannot be empty"
    
    if len(name.strip()) > 100:
        return False, "Project name too long (max 100 characters)"
    
    return True, ""

def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """Валидирует API ключ"""
    if not api_key or not api_key.strip():
        return False, "API key is required"
    
    if len(api_key.strip()) < 10:
        return False, "Invalid API key format"
    
    return True, ""

def validate_workspace_id(workspace_id: str) -> Tuple[bool, str]:
    """Валидирует ID рабочего пространства"""
    if not workspace_id or not workspace_id.strip():
        return False, "Workspace ID is required"
    
    return True, ""

def validate_user_id(user_id: str) -> Tuple[bool, str]:
    """Валидирует ID пользователя"""
    if not user_id or not user_id.strip():
        return False, "User ID is required"
    
    return True, ""
