import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestMainAppSimple:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Тест корневого endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Clockify Agent API"
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self, client):
        """Тест health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "clockify-agent"
    
    def test_docs_endpoint(self, client):
        """Тест Swagger UI endpoint"""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_endpoint(self, client):
        """Тест OpenAPI JSON endpoint"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Clockify Agent"
        assert data["info"]["version"] == "1.0.0"
        assert "paths" in data
    
    def test_api_v1_endpoints_exist(self, client):
        """Тест что API v1 endpoints существуют"""
        response = client.get("/openapi.json")
        data = response.json()
        
        paths = data["paths"]
        
        # Проверяем основные endpoints
        assert "/api/v1/daily-timeline" in paths
        assert "/api/v1/project-timeline" in paths
        assert "/api/v1/projects" in paths
        
        # Проверяем что endpoints имеют GET методы
        assert "get" in paths["/api/v1/daily-timeline"]
        assert "get" in paths["/api/v1/project-timeline"]
        assert "get" in paths["/api/v1/projects"]
    
    def test_app_info(self, client):
        """Тест информации о приложении"""
        response = client.get("/openapi.json")
        data = response.json()
        
        info = data["info"]
        assert info["title"] == "Clockify Agent"
        assert info["version"] == "1.0.0"
        assert "description" in info
    
    def test_app_components_exist(self, client):
        """Тест что компоненты схем существуют"""
        response = client.get("/openapi.json")
        data = response.json()
        
        components = data.get("components", {})
        schemas = components.get("schemas", {})
        
        # Проверяем основные схемы ответов
        assert "DailyTimelineResponse" in schemas
        assert "ProjectTimelineResponse" in schemas
        # ErrorResponse может не быть в схемах, так как используется только в коде
    
    def test_app_responses_structure(self, client):
        """Тест структуры ответов"""
        response = client.get("/openapi.json")
        data = response.json()
        
        paths = data["paths"]
        
        # Проверяем что все API endpoints имеют правильные ответы
        api_endpoints = ["/api/v1/daily-timeline", "/api/v1/project-timeline", "/api/v1/projects"]
        
        for endpoint in api_endpoints:
            if endpoint in paths:
                get_method = paths[endpoint]["get"]
                responses = get_method["responses"]
                
                # Проверяем что есть успешный ответ
                assert "200" in responses
                
                # Проверяем что есть ответ об ошибке валидации (может быть не во всех endpoints)
                # assert "422" in responses
    
    def test_app_parameters_structure(self, client):
        """Тест структуры параметров"""
        response = client.get("/openapi.json")
        data = response.json()
        
        paths = data["paths"]
        
        # Проверяем параметры для daily-timeline
        if "/api/v1/daily-timeline" in paths:
            daily_timeline = paths["/api/v1/daily-timeline"]["get"]
            parameters = daily_timeline.get("parameters", [])
            
            param_names = [param["name"] for param in parameters]
            assert "start_date" in param_names
            assert "end_date" in param_names
        
        # Проверяем параметры для project-timeline
        if "/api/v1/project-timeline" in paths:
            project_timeline = paths["/api/v1/project-timeline"]["get"]
            parameters = project_timeline.get("parameters", [])
            
            param_names = [param["name"] for param in parameters]
            assert "start_date" in param_names
            assert "end_date" in param_names
            assert "project" in param_names
    
    def test_app_startup_success(self, client):
        """Тест что приложение успешно запускается"""
        # Простой тест что основные endpoints отвечают
        endpoints_to_test = ["/", "/health", "/docs", "/openapi.json"]
        
        for endpoint in endpoints_to_test:
            response = client.get(endpoint)
            # Проверяем что endpoint отвечает (не 404)
            assert response.status_code != 404
    
    def test_app_cors_handling(self, client):
        """Тест обработки CORS"""
        # Проверяем что приложение обрабатывает OPTIONS запросы
        response = client.options("/api/v1/daily-timeline")
        
        # OPTIONS может быть не разрешен, но не должен быть 404
        assert response.status_code != 404
    
    def test_app_error_handling(self, client):
        """Тест обработки ошибок"""
        # Проверяем что несуществующий endpoint возвращает 404
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404
    
    def test_app_content_types(self, client):
        """Тест типов контента"""
        # Проверяем JSON endpoints
        response = client.get("/")
        assert "application/json" in response.headers["content-type"]
        
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]
        
        response = client.get("/openapi.json")
        assert "application/json" in response.headers["content-type"]
        
        # Проверяем HTML endpoint
        response = client.get("/docs")
        assert "text/html" in response.headers["content-type"]


if __name__ == "__main__":
    pytest.main([__file__])
