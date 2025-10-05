from datetime import datetime, timedelta
from typing import List, Tuple
import structlog
from app.core.config import settings

logger = structlog.get_logger()

def format_duration(hours: float) -> str:
    """Конвертирует 18.2 часа в '18h 12m'"""
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h}h {m}m"

def parse_clockify_time(iso_string: str) -> datetime:
    """Парсит ISO строку времени из Clockify API и конвертирует в локальный часовой пояс"""
    try:
        # Handle both with and without microseconds
        if '.' in iso_string:
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        
        # Конвертируем из UTC в локальный часовой пояс
        # Если TIMEZONE_OFFSET=3, то добавляем 3 часа к UTC чтобы получить локальное время GMT+3
        local_dt = dt + timedelta(hours=settings.timezone_offset)
        
        return local_dt
    except ValueError as e:
        logger.error("Failed to parse time", time_string=iso_string, error=str(e))
        raise ValueError(f"Invalid time format: {iso_string}")

def calculate_duration(start: datetime, end: datetime) -> str:
    """Рассчитывает длительность между двумя временными точками в формате HH:MM:SS"""
    duration = end - start
    total_seconds = int(duration.total_seconds())
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def calculate_hours(start: datetime, end: datetime) -> float:
    """Рассчитывает количество часов между двумя временными точками"""
    duration = end - start
    return round(duration.total_seconds() / 3600, 1)

def format_time_only(dt: datetime) -> str:
    """Форматирует время в формат HH:MM"""
    return dt.strftime("%H:%M")

def merge_adjacent_blocks(blocks: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
    """Объединяет соседние временные блоки (gap < 5 минут)"""
    if not blocks:
        return []
    
    # Sort by start time
    sorted_blocks = sorted(blocks, key=lambda x: x[0])
    merged = [sorted_blocks[0]]
    
    for current_start, current_end in sorted_blocks[1:]:
        last_start, last_end = merged[-1]
        
        # Check if gap is less than 5 minutes
        gap = (current_start - last_end).total_seconds() / 60
        if gap <= 5:
            # Merge blocks
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append((current_start, current_end))
    
    return merged

def format_session_duration(hours: float) -> str:
    """Форматирует длительность сессии в формат HH:MM:SS"""
    h = int(hours)
    m = int((hours - h) * 60)
    s = int(((hours - h) * 60 - m) * 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
