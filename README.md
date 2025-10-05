# Clockify Agent

Микросервис для получения временных данных из Clockify в формате timeline.

## Возможности

- **Daily Timeline**: Временная шкала по дням и проектам
- **Project Timeline**: Временная шкала для конкретного проекта  
- **Описания**: Отображение описаний того, что делалось во время работы
- **Автообъединение**: Соседние блоки объединяются (gap < 5 мин)
- **Часовой пояс**: Настраиваемое отображение времени
- **Фильтрация**: Показывает только активные проекты

## Технологии

- **FastAPI** - Веб-фреймворк для API
- **Pydantic** - Валидация данных и сериализация
- **httpx** - Асинхронные HTTP запросы к Clockify API
- **structlog** - Структурированное логирование
- **pytest** - Тестирование с покрытием кода

## Установка

```bash
# 1. Клонирование
git clone <repository-url>
cd Clockify-agent

# 2. Настройка окружения
cp .env.example .env
# Отредактируйте .env с вашими данными Clockify

# 3. Установка зависимостей
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Запуск
python run.py
```

## Конфигурация

```env
# Clockify API
CLOCKIFY_API_KEY=your_api_key_here
CLOCKIFY_WORKSPACE_ID=your_workspace_id_here
CLOCKIFY_USER_ID=your_user_id_here

# Настройки
TIMEZONE_OFFSET=3  # GMT+3 для Москвы
MAX_PERIOD_DAYS=31
```

## API Endpoints

### Daily Timeline
```bash
GET /api/v1/daily-timeline?start_date=2024-10-21&end_date=2024-10-27
```

**Ответ:**
```json
{
  "days": {
    "2024-10-21": {
      "projects": {
        "Job": {
          "total_hours": 2.5,
          "time_blocks": [
            {
              "start_time": "10:30",
              "end_time": "11:03",
              "duration": "00:33:05",
              "description": "Авторизация"
            }
          ]
        }
      },
      "day_total": 2.5
    }
  },
  "summary": {
    "period": "2024-10-21 to 2024-10-27",
    "active_days": 5,
    "total_time": "25h 30m",
    "project_totals": {
      "Job": {
        "hours": 18.2,
        "formatted": "18h 12m"
      }
    }
  }
}
```

### Project Timeline
```bash
GET /api/v1/project-timeline?start_date=2024-10-21&end_date=2024-10-27&project=Job
```

### List Projects
```bash
GET /api/v1/projects
```

## Примеры использования

### Получение данных за неделю
```bash
curl "http://localhost:8000/api/v1/daily-timeline?start_date=2024-10-21&end_date=2024-10-27"
```

### Анализ конкретного проекта
```bash
curl "http://localhost:8000/api/v1/project-timeline?start_date=2024-10-21&end_date=2024-10-27&project=Job"
```

### Список всех проектов
```bash
curl "http://localhost:8000/api/v1/projects"
```

## Тестирование

```bash
make test          # Запуск всех тестов
make test-coverage # С покрытием кода
make test-verbose  # Подробный вывод
```

**Покрытие кода**: 70% (88 тестов)

### Структура тестов

- **`test_api.py`** - API endpoints и обработка ошибок (11 тестов)
- **`test_basic.py`** - Утилиты и валидаторы (12 тестов)  
- **`test_schemas.py`** - Pydantic модели запросов (44 теста)
- **`test_clockify_client_simple.py`** - Clockify клиент (9 тестов)
- **`test_timeline_service_simple.py`** - Timeline сервис (10 тестов)
- **`test_main_simple.py`** - Основное приложение (12 тестов)

### Компоненты с полным покрытием

- ✅ **Схемы запросов** (`app/schemas/request.py`) - 100%
- ✅ **Схемы ответов** (`app/schemas/response.py`) - 100%
- ✅ **Clockify модели** (`app/schemas/clockify.py`) - 100%
- ✅ **Конфигурация** (`app/core/config.py`) - 100%
- ✅ **Форматирование времени** (`app/utils/time_formatter.py`) - 92%
- ✅ **Валидаторы** (`app/utils/validators.py`) - 91%

## Разработка

### Структура проекта
```
app/
├── core/           # Конфигурация
├── routers/        # API endpoints
├── schemas/        # Pydantic модели
├── services/       # Бизнес-логика
└── utils/          # Утилиты
```

### Команды разработки
```bash
make install       # Установка зависимостей
make test          # Запуск тестов
make test-coverage # Тесты с покрытием
make clean         # Очистка кэша
make run           # Запуск приложения
```

## Документация

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Тестирование**: Комплексное покрытие всех компонентов

## Настройка часового пояса

`TIMEZONE_OFFSET` - смещение в часах от UTC:
- `0` - UTC (по умолчанию)
- `3` - GMT+3 (Москва)
- `-5` - GMT-5 (Нью-Йорк)

**Пример:** 06:55 UTC → 09:55 GMT+3 (с `TIMEZONE_OFFSET=3`)

## Обработка ошибок

```json
{
  "error": "Invalid date format",
  "message": "Date must be in YYYY-MM-DD format",
  "code": "INVALID_DATE_FORMAT"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Invalid input
- `404` - Project not found
- `401` - Invalid API key
- `500` - Server error

## Лицензия

MIT License - свободное использование и модификация.

## Поддержка

При возникновении проблем:
1. Проверьте конфигурацию в `.env`
2. Убедитесь что API ключ Clockify действителен
3. Проверьте логи приложения
4. Запустите тесты: `make test`