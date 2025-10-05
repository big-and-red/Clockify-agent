# Clockify Agent

Микросервис для получения временных данных из Clockify в формате timeline.

## Возможности

- **Daily Timeline**: Временная шкала по дням и проектам
- **Project Timeline**: Временная шкала для конкретного проекта  
- **Описания**: Отображение описаний того, что делалось во время работы
- **Автообъединение**: Соседние блоки объединяются (gap < 5 мин)
- **Часовой пояс**: Настраиваемое отображение времени

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
TIMEZONE_OFFSET=3  # GMT+3 для Москвы/Минска
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

## Тестирование

```bash
make test          # Запуск всех тестов
make test-coverage # С покрытием кода
make test-verbose  # Подробный вывод
```

**Покрытие кода**: 63% (23 теста)

## Документация

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Тестирование**: [TESTING.md](TESTING.md)

## Настройка часового пояса

`TIMEZONE_OFFSET` - смещение в часах от UTC:
- `0` - UTC (по умолчанию)
- `3` - GMT+3 (Москва, Минск)
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