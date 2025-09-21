# Конструктор Telegram ботов

## Описание

Конструктор Telegram ботов с визуальным редактором сценариев и поддержкой различных типов блоков.

## Основные возможности

- Визуальный редактор сценариев с drag-and-drop интерфейсом
- Поддержка различных типов блоков:
  - Стартовый блок
  - Текстовые сообщения
  - Изображения
  - Кнопки
  - Inline-кнопки
  - Условия
  - Переменные
  - HTTP-запросы
  - Меню
- Экспорт ботов в ZIP-архив для развертывания
- Импорт ботов из ZIP-архива
- Запуск ботов прямо из интерфейса

## Требования

- Python 3.8+
- Node.js 14+
- Telegram Bot Token

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd telegram-bot-constructor
   ```

2. Установите зависимости бэкенда:
   ```bash
   pip install -r requirements.txt
   ```

3. Установите зависимости фронтенда:
   ```bash
   cd frontend
   npm install
   ```

## Запуск

1. Запустите бэкенд:
   ```bash
   python main.py
   ```

2. Запустите фронтенд:
   ```bash
   cd frontend
   npm start
   ```

## Безопасность

Подробная информация о мерах безопасности и хранении токенов находится в файле [SECURITY.md](SECURITY.md).

## Конфигурация

### Переменные окружения

Создайте файл `.env` в корневой директории проекта:

```env
# Обязательные переменные
ENVIRONMENT=development  # или production

# Опциональные переменные
BOT_TOKEN=your_bot_token  # общий токен для всех ботов
BOT_TOKEN_MAINBOT=your_main_bot_token  # токен для конкретного бота
```

### Для продакшена

В продакшене рекомендуется:
1. Установить `ENVIRONMENT=production`
2. Хранить токены только в переменных окружения
3. Не использовать файлы токенов

## Структура проекта

```
telegram-bot-constructor/
├── main.py              # Бэкенд (FastAPI)
├── bots/                # Директория для сохраненных сценариев
├── blocks/              # Блоки для визуального редактора
├── core/                # Ядро системы
├── frontend/            # Фронтенд (React)
├── requirements.txt     # Зависимости Python
└── SECURITY.md          # Документация по безопасности
```

## API эндпоинты

### Боты
- `GET /api/get_bots/` - Получить список всех ботов
- `POST /api/create_bot/{bot_id}/` - Создать нового бота
- `DELETE /api/delete_bot/{bot_id}/` - Удалить бота
- `POST /api/rename_bot/{old_bot_id}/{new_bot_id}/` - Переименовать бота

### Сценарии
- `GET /api/get_scenario/{bot_id}/` - Получить сценарий бота
- `POST /api/save_scenario/{bot_id}/` - Сохранить сценарий бота

### Токены
- `GET /api/get_token/{bot_id}/` - Получить токен бота
- `POST /api/save_token/{bot_id}/` - Сохранить токен бота (только в разработке)
- `DELETE /api/delete_token/{bot_id}/` - Удалить токен бота (только в разработке)
- `GET /api/check_token/{token}/` - Проверить токен
- `GET /api/check_bot/{token}/` - Проверить доступность бота

### Имена ботов
- `GET /api/get_bot_name/{bot_id}/` - Получить имя бота
- `POST /api/set_bot_name/{bot_id}/` - Установить имя бота

### Запуск/остановка
- `POST /api/run_bot/{bot_id}/` - Запустить бота
- `GET /api/stop_bot/{bot_id}/` - Остановить бота
- `GET /api/bot_running_status/{bot_id}/` - Проверить статус бота

### Система
- `GET /api/available_blocks/` - Получить список доступных блоков
- `GET /api/health/` - Проверить состояние системы
- `GET /api/bot_status/` - Получить статус всех ботов

## Экспорт/импорт
- `POST /api/import_bot/` - Импортировать бота
- `POST /api/export_bot_zip/{bot_id}/` - Экспортировать бота в ZIP

## Лицензия

MIT