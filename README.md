(Due to technical issues, the search service is temporarily unavailable.)

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