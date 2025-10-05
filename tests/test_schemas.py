import pytest
from pydantic import ValidationError
from app.schemas.request import DailyTimelineRequest, ProjectTimelineRequest, ErrorResponse


class TestRequestSchemas:
    
    def test_daily_timeline_request_valid(self):
        """Тест валидного запроса daily timeline"""
        request = DailyTimelineRequest(
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        assert request.start_date == "2024-01-01"
        assert request.end_date == "2024-01-31"
    
    def test_daily_timeline_request_invalid_date_format(self):
        """Тест невалидного формата даты"""
        with pytest.raises(ValidationError) as exc_info:
            DailyTimelineRequest(
                start_date="01-01-2024",  # Неправильный формат
                end_date="2024-01-31"
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "value_error"
        assert "Date must be in YYYY-MM-DD format" in str(errors[0]["msg"])
    
    def test_daily_timeline_request_invalid_date_value(self):
        """Тест невалидного значения даты"""
        with pytest.raises(ValidationError) as exc_info:
            DailyTimelineRequest(
                start_date="2024-13-01",  # Несуществующий месяц
                end_date="2024-01-31"
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "value_error"
    
    def test_project_timeline_request_valid(self):
        """Тест валидного запроса project timeline"""
        request = ProjectTimelineRequest(
            start_date="2024-01-01",
            end_date="2024-01-31",
            project="Test Project"
        )
        assert request.start_date == "2024-01-01"
        assert request.end_date == "2024-01-31"
        assert request.project == "Test Project"
    
    def test_project_timeline_request_empty_project(self):
        """Тест пустого названия проекта"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectTimelineRequest(
                start_date="2024-01-01",
                end_date="2024-01-31",
                project=""  # Пустое название
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "value_error"
        assert "Project name cannot be empty" in str(errors[0]["msg"])
    
    def test_project_timeline_request_whitespace_project(self):
        """Тест проекта с пробелами"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectTimelineRequest(
                start_date="2024-01-01",
                end_date="2024-01-31",
                project="   "  # Только пробелы
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "value_error"
        assert "Project name cannot be empty" in str(errors[0]["msg"])
    
    def test_project_timeline_request_project_trimming(self):
        """Тест обрезки пробелов в названии проекта"""
        request = ProjectTimelineRequest(
            start_date="2024-01-01",
            end_date="2024-01-31",
            project="  Test Project  "  # С пробелами
        )
        assert request.project == "Test Project"  # Пробелы обрезаны
    
    def test_project_timeline_request_multiple_errors(self):
        """Тест множественных ошибок валидации"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectTimelineRequest(
                start_date="01-01-2024",  # Неправильный формат
                end_date="2024-13-01",    # Неправильная дата
                project=""               # Пустое название
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 3  # Все три ошибки
    
    def test_error_response_valid(self):
        """Тест валидного ответа об ошибке"""
        error = ErrorResponse(
            error="Test Error",
            message="Test message",
            code="TEST_ERROR"
        )
        assert error.error == "Test Error"
        assert error.message == "Test message"
        assert error.code == "TEST_ERROR"
    
    def test_error_response_empty_fields(self):
        """Тест ответа об ошибке с пустыми полями"""
        error = ErrorResponse(
            error="",
            message="",
            code=""
        )
        assert error.error == ""
        assert error.message == ""
        assert error.code == ""
    
    @pytest.mark.parametrize("start_date,end_date", [
        ("2024-01-01", "2024-01-31"),
        ("2024-12-31", "2024-12-31"),
        ("2023-02-28", "2023-02-28"),  # Не високосный год
        ("2024-02-29", "2024-02-29"),  # Високосный год
    ])
    def test_daily_timeline_request_valid_dates(self, start_date, end_date):
        """Тест различных валидных дат"""
        request = DailyTimelineRequest(
            start_date=start_date,
            end_date=end_date
        )
        assert request.start_date == start_date
        assert request.end_date == end_date
    
    @pytest.mark.parametrize("invalid_date", [
        "2024-13-01",  # Несуществующий месяц
        "2024-01-32",  # Несуществующий день
        "2024-02-30",  # 30 февраля
        "2023-02-29",  # 29 февраля в невисокосный год
        "2024-04-31",  # 31 апреля
        "2024-06-31",  # 31 июня
        "2024-09-31",  # 31 сентября
        "2024-11-31",  # 31 ноября
    ])
    def test_daily_timeline_request_invalid_dates(self, invalid_date):
        """Тест различных невалидных дат"""
        with pytest.raises(ValidationError):
            DailyTimelineRequest(
                start_date=invalid_date,
                end_date="2024-01-31"
            )
    
    @pytest.mark.parametrize("project_name", [
        "Test Project",
        "Project with numbers 123",
        "Project-with-dashes",
        "Project_with_underscores",
        "Project.with.dots",
        "Project with spaces",
        "a",  # Минимальная длина
        "a" * 100,  # Максимальная длина
    ])
    def test_project_timeline_request_valid_project_names(self, project_name):
        """Тест различных валидных названий проектов"""
        request = ProjectTimelineRequest(
            start_date="2024-01-01",
            end_date="2024-01-31",
            project=project_name
        )
        assert request.project == project_name
    
    def test_daily_timeline_request_missing_fields(self):
        """Тест отсутствующих полей в daily timeline request"""
        with pytest.raises(ValidationError) as exc_info:
            DailyTimelineRequest()
        
        errors = exc_info.value.errors()
        assert len(errors) == 2  # start_date и end_date
        field_names = [error["loc"][0] for error in errors]
        assert "start_date" in field_names
        assert "end_date" in field_names
    
    def test_project_timeline_request_missing_fields(self):
        """Тест отсутствующих полей в project timeline request"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectTimelineRequest()
        
        errors = exc_info.value.errors()
        assert len(errors) == 3  # start_date, end_date, project
        field_names = [error["loc"][0] for error in errors]
        assert "start_date" in field_names
        assert "end_date" in field_names
        assert "project" in field_names


if __name__ == "__main__":
    pytest.main([__file__])
