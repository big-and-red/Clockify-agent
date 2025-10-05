import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from app.services.timeline_service import TimelineService


class TestTimelineServiceSimple:
    
    def test_service_initialization(self):
        """Тест инициализации сервиса"""
        with patch('app.services.timeline_service.ClockifyClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            service = TimelineService()
            
            assert service is not None
            assert service.clockify_client is not None
            assert service.clockify_client == mock_client
    
    def test_merge_adjacent_blocks_with_descriptions_empty(self):
        """Тест объединения пустого списка блоков"""
        with patch('app.services.timeline_service.ClockifyClient'):
            service = TimelineService()
            
            result = service._merge_adjacent_blocks_with_descriptions([])
            assert result == []
    
    def test_merge_adjacent_blocks_with_descriptions_single(self):
        """Тест объединения одного блока"""
        with patch('app.services.timeline_service.ClockifyClient'):
            service = TimelineService()
            
            blocks = [
                (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 10, 0), "Task 1")
            ]
            
            result = service._merge_adjacent_blocks_with_descriptions(blocks)
            assert len(result) == 1
            assert result[0][2] == "Task 1"
    
    def test_merge_adjacent_blocks_with_descriptions_two_adjacent(self):
        """Тест объединения двух соседних блоков"""
        with patch('app.services.timeline_service.ClockifyClient'):
            service = TimelineService()
            
            blocks = [
                (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 10, 0), "Task 1"),
                (datetime(2024, 1, 1, 10, 2), datetime(2024, 1, 1, 11, 0), "Task 2")  # Gap 2 мин
            ]
            
            result = service._merge_adjacent_blocks_with_descriptions(blocks)
            assert len(result) == 1  # Объединятся
            assert result[0][2] == "Task 1, Task 2"
    
    def test_merge_adjacent_blocks_with_descriptions_two_separate(self):
        """Тест двух отдельных блоков"""
        with patch('app.services.timeline_service.ClockifyClient'):
            service = TimelineService()
            
            blocks = [
                (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 10, 0), "Task 1"),
                (datetime(2024, 1, 1, 11, 0), datetime(2024, 1, 1, 12, 0), "Task 2")  # Gap 1 час
            ]
            
            result = service._merge_adjacent_blocks_with_descriptions(blocks)
            assert len(result) == 2  # Не объединятся
            assert result[0][2] == "Task 1"
            assert result[1][2] == "Task 2"
    
    def test_merge_adjacent_blocks_with_none_descriptions(self):
        """Тест объединения блоков с None описаниями"""
        with patch('app.services.timeline_service.ClockifyClient'):
            service = TimelineService()
            
            blocks = [
                (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 10, 0), None),
                (datetime(2024, 1, 1, 10, 2), datetime(2024, 1, 1, 11, 0), "Task 2")
            ]
            
            result = service._merge_adjacent_blocks_with_descriptions(blocks)
            assert len(result) == 1
            assert result[0][2] == "Task 2"
    
    def test_merge_adjacent_blocks_with_mixed_descriptions(self):
        """Тест объединения блоков со смешанными описаниями"""
        with patch('app.services.timeline_service.ClockifyClient'):
            service = TimelineService()
            
            blocks = [
                (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 10, 0), "Task 1"),
                (datetime(2024, 1, 1, 10, 2), datetime(2024, 1, 1, 11, 0), None),
                (datetime(2024, 1, 1, 11, 2), datetime(2024, 1, 1, 12, 0), "Task 3")
            ]
            
            result = service._merge_adjacent_blocks_with_descriptions(blocks)
            assert len(result) == 1  # Все три объединятся в один блок
            assert result[0][2] == "Task 1, Task 3"  # Только не-None описания
    
    def test_calculate_daily_summary_empty(self):
        """Тест расчета сводки для пустых данных"""
        with patch('app.services.timeline_service.ClockifyClient'):
            service = TimelineService()
            
            summary = service._calculate_daily_summary(
                {},  # Пустые данные
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31)
            )
            
            assert summary.active_days == 0
            assert summary.total_time == "0h 0m"
            assert summary.project_totals == {}
    
    def test_calculate_project_summary_empty(self):
        """Тест расчета сводки проекта для пустых данных"""
        with patch('app.services.timeline_service.ClockifyClient'):
            service = TimelineService()
            
            summary = service._calculate_project_summary(
                {},  # Пустые данные
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31)
            )
            
            assert summary.active_days == 0
            assert summary.total_time == "0h 0m"
            assert summary.avg_daily == "0h 0m"
            assert summary.longest_session == "00:00:00"
            assert summary.avg_session == "00:00:00"
    
    def test_service_has_required_methods(self):
        """Тест что сервис имеет необходимые методы"""
        with patch('app.services.timeline_service.ClockifyClient'):
            service = TimelineService()
            
            # Проверяем что основные методы существуют
            assert hasattr(service, 'get_daily_timeline')
            assert hasattr(service, 'get_project_timeline')
            assert hasattr(service, '_merge_adjacent_blocks_with_descriptions')
            assert hasattr(service, '_calculate_daily_summary')
            assert hasattr(service, '_calculate_project_summary')
            
            # Проверяем что методы являются callable
            assert callable(service.get_daily_timeline)
            assert callable(service.get_project_timeline)
            assert callable(service._merge_adjacent_blocks_with_descriptions)
            assert callable(service._calculate_daily_summary)
            assert callable(service._calculate_project_summary)
    
    def test_service_clockify_client_integration(self):
        """Тест интеграции с ClockifyClient"""
        with patch('app.services.timeline_service.ClockifyClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            service = TimelineService()
            
            # Проверяем что сервис использует правильный клиент
            assert service.clockify_client == mock_client
            
            # Проверяем что клиент имеет необходимые методы
            assert hasattr(mock_client, 'get_time_entries')
            assert hasattr(mock_client, 'get_projects')
            assert hasattr(mock_client, 'get_project_by_name')


if __name__ == "__main__":
    pytest.main([__file__])
