import requests
import random
import time
from time import sleep

# Правильный URL для отправки
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfmmXQ2njhAvbfIJaK9ODQWr9uBYi9mHFKre-6z301Emo2O1w/formResponse"

# ОБНОВЛЕННЫЕ идентификаторы полей на основе ваших данных
FIELD_NAMES = {
    "child": "entry.497677583",      # Чей ты ребенок (entry.497677583)
    "ava": "entry.832250359",        # ава (entry.832250359)
    "pranks": "entry.1793887257",    # приколы (entry.1793887257)
    "pranks_other": "entry.1793887257.other_option_response"
}

# Генераторы случайных ответов
def random_child():
    return random.choice(["Вариант 1", "Вариант 2"])

def random_ava():
    texts = ["Да", "Нет", "Может быть", "я не знаю, как", "Случайный текст"]
    return random.choice(texts)

def random_pranks():
    choice = random.choice(["option", "other"])
    if choice == "option":
        return random.choice(["Вариант 1", "Вариант 2", "Вариант 3"]), None
    else:
        return "__other_option__", f"Свой вариант {random.randint(1,1000)}"

# Технические параметры из ваших данных
FBZX = "-5276659025385767459"  # fbzx значение
PAGE_HISTORY = "0"             # pageHistory

# Отправка 300 ответов
for i in range(1, 301):
    # Генерация ответов
    child_answer = random_child()
    ava_answer = random_ava()
    pranks_answer, pranks_other = random_pranks()
    
    # Формирование данных
    form_data = {
        FIELD_NAMES['child']: child_answer,
        FIELD_NAMES['ava']: ava_answer,
        FIELD_NAMES['pranks']: pranks_answer,
        
        # Технические параметры
        "fvv": "1",
        "draftResponse": '[]',
        "pageHistory": PAGE_HISTORY,
        "fbzx": FBZX
    }
    
    # Добавляем поле для "Другое" если нужно
    if pranks_other:
        form_data[FIELD_NAMES['pranks_other']] = pranks_other

    try:
        # Добавляем заголовки
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://docs.google.com/forms/d/e/1FAIpQLSfmmXQ2njhAvbfIJaK9ODQWr9uBYi9mHFKre-6z301Emo2O1w/viewform',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(FORM_URL, data=form_data, headers=headers)
        
        # Проверяем успешность
        if response.status_code == 200:
            print(f"Отправка {i}/300: Успешно!")
        else:
            print(f"Ошибка при отправке {i}: {response.status_code} - {response.reason}")
            
    except Exception as e:
        print(f"Ошибка при отправке {i}: {str(e)}")
    
    # Пауза для избежания блокировки
    sleep(random.uniform(1.0, 3.0))

print("Все ответы отправлены!")