# MVP. Social-version

# Skill Exchange Platform

## Настройка базы данных

1. Создайте базу данных PostgreSQL:
```sql
CREATE DATABASE skillswap;
```

2. Создайте пользователя и назначьте права:
```sql
CREATE USER skilluser WITH PASSWORD 'skillpass';
GRANT ALL PRIVILEGES ON DATABASE skillswap TO skilluser;
```

3. Подключитесь к базе данных:
```bash
psql -d skillswap -U skilluser
```

4. Выполните SQL-скрипт для создания таблиц:
```bash
psql -d skillswap -U skilluser -f create_tables.sql
```

## Структура базы данных

### Таблица users
- id: SERIAL PRIMARY KEY
- email: VARCHAR(255) UNIQUE NOT NULL
- password_hash: VARCHAR(255) NOT NULL
- first_name: VARCHAR(100) NOT NULL
- last_name: VARCHAR(100) NOT NULL
- birth_date: DATE NOT NULL
- location: VARCHAR(255) NOT NULL
- photo_path: VARCHAR(255) DEFAULT '/static/images/default-avatar.jpg'
- teach_skills: TEXT[]
- learn_skills: TEXT[]
- languages: TEXT[]
- interests: TEXT[]
- work_place: VARCHAR(255)
- study_place: VARCHAR(255)
- about: TEXT
- social_vk: VARCHAR(255)
- social_tg: VARCHAR(255)
- social_gh: VARCHAR(255)
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Таблица password_reset_tokens
- id: SERIAL PRIMARY KEY
- user_id: INTEGER REFERENCES users(id)
- token: VARCHAR(255) NOT NULL
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- expires_at: TIMESTAMP NOT NULL
- used: BOOLEAN DEFAULT FALSE

### Таблица reviews
- id: SERIAL PRIMARY KEY
- reviewer_id: INTEGER REFERENCES users(id)
- reviewed_id: INTEGER REFERENCES users(id)
- rating: INTEGER CHECK (rating >= 1 AND rating <= 5)
- comment: TEXT
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Таблица exchanges
- id: SERIAL PRIMARY KEY
- user_id: INTEGER REFERENCES users(id)
- title: VARCHAR(255) NOT NULL
- description: TEXT
- status: VARCHAR(50) DEFAULT 'active'
- progress: INTEGER DEFAULT 0
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Таблица available_slots
- id: SERIAL PRIMARY KEY
- user_id: INTEGER REFERENCES users(id)
- start_time: TIMESTAMP NOT NULL
- end_time: TIMESTAMP NOT NULL
- is_booked: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Настройка приложения

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл с переменными окружения:
```bash
cp .env.example .env
```

3. Настройте переменные окружения в файле .env:
```
FLASK_APP=app-v4.py
FLASK_ENV=development
DATABASE_URL=postgresql://skilluser:skillpass@localhost/skillswap
SECRET_KEY=your-secret-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

4. Запустите приложение:
```bash
flask run
```

## Функциональность

- Регистрация и авторизация пользователей
- Восстановление пароля через email
- Просмотр и редактирование профиля
- Загрузка фотографии профиля
- Добавление и редактирование навыков
- Система отзывов
- Календарь доступных слотов
- Система обмена навыками
- Уведомления

```markdown
# Инструкция по запуску Flask-приложения

## Предварительные требования
- Установленный Python 3.6+
- Менеджер пакетов `pip`

## 1. Установка зависимостей
Создайте файл `requirements.txt` в корне проекта и добавьте:
```txt
Flask>=2.0.0
```

## 2. Настройка виртуального окружения
### Для macOS/Linux:
```bash
python3 -m venv .venv          # Создать окружение
source .venv/bin/activate      # Активировать
pip install -r requirements.txt # Установить зависимости
```

### Для Windows:
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Запуск приложения
```bash
python app.py
```

Сервер запустится на http://localhost:5000 или http://127.0.0.1:5000.

---

## Если возникают ошибки
### Ошибка "ModuleNotFoundError"
- Убедитесь, что виртуальное окружение активировано (в терминале должно быть `(.venv)` в начале строки).
- Переустановите зависимости:
  ```bash
  pip uninstall Flask
  pip install -r requirements.txt
  ```

### Приложение не запускается
- Проверьте, что файл `app.py` существует и находится в корне проекта.
- Убедитесь, что порт 5000 не занят другой программой.

---

> **Примечание:** Для выхода из виртуального окружения выполните `deactivate`.
```