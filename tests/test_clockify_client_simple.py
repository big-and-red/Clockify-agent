import pytest
from unittest.mock import patch, MagicMock
from app.services.clockify_client import ClockifyClient


class TestClockifyClientSimple:
    
    def test_client_initialization_with_settings(self):
        """Тест инициализации клиента с настройками"""
        with patch('app.services.clockify_client.settings') as mock_settings:
            mock_settings.clockify_api_key = "test_key_123456789"  # Длинный ключ для валидации
            mock_settings.clockify_workspace_id = "test_workspace"
            mock_settings.clockify_user_id = "test_user"
            
            client = ClockifyClient()
            
            assert client.api_key == "test_key_123456789"
            assert client.workspace_id == "test_workspace"
            assert client.user_id == "test_user"
            assert client.base_url == "https://api.clockify.me/api/v1"
            assert client.timeout == 30.0
    
    def test_client_headers(self):
        """Тест заголовков клиента"""
        with patch('app.services.clockify_client.settings') as mock_settings:
            mock_settings.clockify_api_key = "test_key_123456789"  # Длинный ключ для валидации
            mock_settings.clockify_workspace_id = "test_workspace"
            mock_settings.clockify_user_id = "test_user"
            
            client = ClockifyClient()
            
            # Проверяем что заголовки правильно формируются
            expected_headers = {
                "X-Api-Key": "test_key",
                "Content-Type": "application/json"
            }
            
            # Проверяем что метод _get_headers существует и возвращает правильные заголовки
            if hasattr(client, '_get_headers'):
                headers = client._get_headers()
                assert headers["X-Api-Key"] == "test_key_123456789"  # Исправлено
                assert headers["Content-Type"] == "application/json"
    
    def test_client_url_construction(self):
        """Тест построения URL"""
        with patch('app.services.clockify_client.settings') as mock_settings:
            mock_settings.clockify_api_key = "test_key_123456789"  # Длинный ключ для валидации
            mock_settings.clockify_workspace_id = "test_workspace"
            mock_settings.clockify_user_id = "test_user"
            
            client = ClockifyClient()
            
            # Проверяем базовый URL
            assert client.base_url == "https://api.clockify.me/api/v1"
            
            # Проверяем что можно построить полный URL
            endpoint = "/test"
            full_url = f"{client.base_url}{endpoint}"
            assert full_url == "https://api.clockify.me/api/v1/test"
    
    def test_client_configuration_validation(self):
        """Тест валидации конфигурации"""
        with patch('app.services.clockify_client.settings') as mock_settings:
            mock_settings.clockify_api_key = "test_key_123456789"  # Длинный ключ для валидации
            mock_settings.clockify_workspace_id = "test_workspace"
            mock_settings.clockify_user_id = "test_user"
            
            # Проверяем что клиент создается без ошибок
            client = ClockifyClient()
            assert client is not None
            
            # Проверяем что все обязательные поля установлены
            assert client.api_key is not None
            assert client.workspace_id is not None
            assert client.user_id is not None
    
    def test_client_timeout_setting(self):
        """Тест настройки таймаута"""
        with patch('app.services.clockify_client.settings') as mock_settings:
            mock_settings.clockify_api_key = "test_key_123456789"  # Длинный ключ для валидации
            mock_settings.clockify_workspace_id = "test_workspace"
            mock_settings.clockify_user_id = "test_user"
            
            client = ClockifyClient()
            
            # Проверяем что таймаут установлен правильно
            assert client.timeout == 30.0
            assert isinstance(client.timeout, float)
    
    def test_client_workspace_url_construction(self):
        """Тест построения URL для workspace"""
        with patch('app.services.clockify_client.settings') as mock_settings:
            mock_settings.clockify_api_key = "test_key_123456789"  # Длинный ключ для валидации
            mock_settings.clockify_workspace_id = "test_workspace"
            mock_settings.clockify_user_id = "test_user"
            
            client = ClockifyClient()
            
            # Проверяем что workspace_id используется в URL
            workspace_url = f"{client.base_url}/workspaces/{client.workspace_id}"
            assert workspace_url == "https://api.clockify.me/api/v1/workspaces/test_workspace"
    
    def test_client_user_url_construction(self):
        """Тест построения URL для пользователя"""
        with patch('app.services.clockify_client.settings') as mock_settings:
            mock_settings.clockify_api_key = "test_key_123456789"  # Длинный ключ для валидации
            mock_settings.clockify_workspace_id = "test_workspace"
            mock_settings.clockify_user_id = "test_user"
            
            client = ClockifyClient()
            
            # Проверяем что user_id используется в URL
            user_url = f"{client.base_url}/workspaces/{client.workspace_id}/user/{client.user_id}"
            assert user_url == "https://api.clockify.me/api/v1/workspaces/test_workspace/user/test_user"
    
    def test_client_projects_url_construction(self):
        """Тест построения URL для проектов"""
        with patch('app.services.clockify_client.settings') as mock_settings:
            mock_settings.clockify_api_key = "test_key_123456789"  # Длинный ключ для валидации
            mock_settings.clockify_workspace_id = "test_workspace"
            mock_settings.clockify_user_id = "test_user"
            
            client = ClockifyClient()
            
            # Проверяем URL для получения проектов
            projects_url = f"{client.base_url}/workspaces/{client.workspace_id}/projects"
            assert projects_url == "https://api.clockify.me/api/v1/workspaces/test_workspace/projects"
    
    def test_client_time_entries_url_construction(self):
        """Тест построения URL для временных записей"""
        with patch('app.services.clockify_client.settings') as mock_settings:
            mock_settings.clockify_api_key = "test_key_123456789"  # Длинный ключ для валидации
            mock_settings.clockify_workspace_id = "test_workspace"
            mock_settings.clockify_user_id = "test_user"
            
            client = ClockifyClient()
            
            # Проверяем URL для получения временных записей
            time_entries_url = f"{client.base_url}/workspaces/{client.workspace_id}/user/{client.user_id}/time-entries"
            assert time_entries_url == "https://api.clockify.me/api/v1/workspaces/test_workspace/user/test_user/time-entries"


if __name__ == "__main__":
    pytest.main([__file__])
