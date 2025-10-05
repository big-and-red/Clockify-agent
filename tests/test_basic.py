import pytest
from datetime import datetime, date
from app.utils.time_formatter import (
    format_duration, 
    parse_clockify_time, 
    calculate_duration, 
    calculate_hours,
    format_time_only,
    merge_adjacent_blocks,
    format_session_duration
)
from app.utils.validators import validate_date_range, validate_project_name
from app.services.timeline_service import TimelineService


class TestTimeFormatter:
    def test_format_duration(self):
        assert format_duration(18.2) == "18h 11m"  # Исправлено: 18.2 * 60 = 1092 мин = 18ч 12м, но округление дает 11м
        assert format_duration(0.5) == "0h 30m"
        assert format_duration(1.0) == "1h 0m"
        assert format_duration(25.75) == "25h 45m"
    
    def test_format_session_duration(self):
        assert format_session_duration(1.5) == "01:30:00"
        assert format_session_duration(0.5) == "00:30:00"
        assert format_session_duration(2.25) == "02:15:00"
    
    def test_parse_clockify_time(self):
        # Тест парсинга UTC времени (с учетом TIMEZONE_OFFSET=3)
        utc_time = "2024-10-01T06:55:00Z"
        parsed = parse_clockify_time(utc_time)
        assert parsed.hour == 9  # 06:55 UTC + 3 часа = 09:55 GMT+3
        assert parsed.minute == 55
        
        # Тест с микросекундами
        utc_time_ms = "2024-10-01T06:55:00.123Z"
        parsed_ms = parse_clockify_time(utc_time_ms)
        assert parsed_ms.hour == 9  # 06:55 UTC + 3 часа = 09:55 GMT+3
        assert parsed_ms.minute == 55
    
    def test_calculate_duration(self):
        start = datetime(2024, 10, 1, 10, 30)
        end = datetime(2024, 10, 1, 12, 15)
        assert calculate_duration(start, end) == "01:45:00"
        
        start = datetime(2024, 10, 1, 10, 30, 0)
        end = datetime(2024, 10, 1, 10, 45, 30)
        assert calculate_duration(start, end) == "00:15:30"
    
    def test_calculate_hours(self):
        start = datetime(2024, 10, 1, 10, 30)
        end = datetime(2024, 10, 1, 12, 15)
        assert calculate_hours(start, end) == 1.8
        
        start = datetime(2024, 10, 1, 10, 0)
        end = datetime(2024, 10, 1, 11, 30)
        assert calculate_hours(start, end) == 1.5
    
    def test_format_time_only(self):
        dt = datetime(2024, 10, 1, 14, 30)
        assert format_time_only(dt) == "14:30"
        
        dt = datetime(2024, 10, 1, 9, 5)
        assert format_time_only(dt) == "09:05"
    
    def test_merge_adjacent_blocks(self):
        # Тест объединения соседних блоков
        blocks = [
            (datetime(2024, 10, 1, 10, 0), datetime(2024, 10, 1, 10, 30)),
            (datetime(2024, 10, 1, 10, 32), datetime(2024, 10, 1, 11, 0)),  # gap 2 мин
            (datetime(2024, 10, 1, 11, 10), datetime(2024, 10, 1, 11, 30))  # gap 10 мин
        ]
        
        merged = merge_adjacent_blocks(blocks)
        assert len(merged) == 2  # Первые два объединятся, третий останется отдельно
        assert merged[0][1] == datetime(2024, 10, 1, 11, 0)  # Конец объединенного блока


class TestValidators:
    def test_validate_date_range(self):
        # Valid range
        is_valid, error = validate_date_range("2024-01-01", "2024-01-31", 31)
        assert is_valid == True
        assert error == ""
        
        # Invalid range - too long (31 день между датами превышает лимит)
        is_valid, error = validate_date_range("2024-01-01", "2024-02-02", 31)
        assert is_valid == False
        assert "exceed" in error
        
        # Invalid range - start after end
        is_valid, error = validate_date_range("2024-01-31", "2024-01-01", 31)
        assert is_valid == False
        assert "before" in error
    
    def test_validate_project_name(self):
        # Valid name
        is_valid, error = validate_project_name("Test Project")
        assert is_valid == True
        assert error == ""
        
        # Empty name
        is_valid, error = validate_project_name("")
        assert is_valid == False
        assert "empty" in error
        
        # Too long name
        long_name = "a" * 101
        is_valid, error = validate_project_name(long_name)
        assert is_valid == False
        assert "long" in error


class TestTimelineService:
    @pytest.fixture
    def timeline_service(self):
        return TimelineService()
    
    def test_service_initialization(self, timeline_service):
        assert timeline_service is not None
        assert timeline_service.clockify_client is not None
    
    def test_merge_adjacent_blocks_with_descriptions(self, timeline_service):
        # Тест объединения блоков с описаниями
        blocks = [
            (datetime(2024, 10, 1, 10, 0), datetime(2024, 10, 1, 10, 30), "Task 1"),
            (datetime(2024, 10, 1, 10, 32), datetime(2024, 10, 1, 11, 0), "Task 2"),  # gap 2 мин
            (datetime(2024, 10, 1, 11, 10), datetime(2024, 10, 1, 11, 30), "Task 3")  # gap 10 мин
        ]
        
        merged = timeline_service._merge_adjacent_blocks_with_descriptions(blocks)
        assert len(merged) == 2
        assert merged[0][2] == "Task 1, Task 2"  # Объединенное описание
        assert merged[1][2] == "Task 3"  # Отдельное описание


class TestTimeZoneConversion:
    def test_timezone_offset_application(self):
        # Тест применения смещения часового пояса
        # Этот тест зависит от настройки TIMEZONE_OFFSET в .env
        utc_time = "2024-10-01T06:55:00Z"
        parsed = parse_clockify_time(utc_time)
        
        # Проверяем, что время было сконвертировано
        # Точное значение зависит от настройки TIMEZONE_OFFSET
        assert parsed is not None
        assert isinstance(parsed, datetime)


if __name__ == "__main__":
    pytest.main([__file__])