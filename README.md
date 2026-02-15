# Skill Exchange Platform (Vetka) - MVP

Flask-приложение для обмена навыками: пользователи создают профили, указывают навыки (могу научить / хочу научиться), находят людей через поиск, оставляют отзывы, добавляют слоты доступности и договариваются о встречах. Дополнительно: Random Coffee (встречи сообщества) и простой блог с внешними статьями.

# Инструкция по запуску Flask-приложения
## Быстрый старт (Docker: приложение + инфраструктура)

1. Создать `.env`:
```bash
cp .env.example .env
```

2. Поднять сервисы:
```bash
docker compose up --build
```

3. Открыть:
- приложение: http://localhost:5000 (если порт занят: `WEB_PORT=5001 docker compose up --build`)
- SMTP web UI (Mailpit): http://localhost:8025

База данных PostgreSQL поднимается в контейнере `db` и автоматически применяет `create_tables.sql`.

## Локальный запуск (venv; Postgres или SQLite)

1. Виртуальное окружение и зависимости:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Переменные окружения:
```bash
cp .env.example .env
```
Отредактируйте `.env` (минимум: `SECRET_KEY`, `DATABASE_URL` или `DB_*`). Для Postgres из `docker compose` по умолчанию `localhost:5433`. Для быстрой локальной работы без Postgres установите `DB_DIALECT=sqlite` (файл `SQLITE_PATH`, по умолчанию `database.db`).

3. Инфраструктура (если Postgres/SMTP из Docker):
```bash
docker compose up -d db mailpit
```

4. Запуск приложения:
```bash
python app.py
```
Если порт 5000 занят: `PORT=5001 python app.py`.

## Что внутри (снимки интерфейса)

Папка ` screenshots` содержит актуальные скриншоты основных страниц:

- `Main.png`, `Main page.png` — главная.
- `login.png`, `registration.png` — аутентификация.
- `users.png`, `activities.png` — поиск и активность сообщества.
- `Store.png` — магазин/донаты.
- `B2B.png` — раздел для компаний.
- `about project.png`, `comments.png` — блоки «О нас» и отзывы.

Главные экраны:

![Главная](/%20screenshots/Main.png)
![Магазин](/%20screenshots/Store.png)
![B2B](/%20screenshots/B2B.png)

Остальные скриншоты см. прямо в директории ` screenshots`.


## Переменные окружения

- `SECRET_KEY`: секрет для сессий/CSRF (в продакшене обязателен).
- `DATABASE_URL`: строка подключения Postgres `postgresql://user:pass@host:port/db`.
- Альтернатива вместо `DATABASE_URL`: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, опционально `DB_SSLMODE`.
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USE_TLS`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`: отправка писем для сброса пароля.
- `UPLOAD_FOLDER`: папка для аватарок (по умолчанию `static/avatars`).
- `HOST`, `PORT`, `FLASK_DEBUG`: параметры dev-сервера при запуске через `python app.py`.

## Структура проекта

- `app_v4.py`: основной код приложения (Flask `app`).
- `app.py`: точка входа (`python app.py`).
- `create_tables.sql`: схема БД (idempotent, можно запускать повторно).
- `templates/`, `static/`: фронтенд (Jinja + статика).

## Примечания


- `app-v2.py` и `app-v3.py` оставлены как исторические прототипы и не используются текущим запуском.
**Примечание:** Для выхода из виртуального окружения выполните `deactivate`.

