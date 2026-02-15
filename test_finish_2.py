import requests
import random
import time
from bs4 import BeautifulSoup

# URL формы
FORM_VIEW_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfrC4RB0I6-qqHwL0Eb2F2U_73ytmJqYmff2aPqL7Y_r867-A/viewform"
FORM_SUBMIT_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfrC4RB0I6-qqHwL0Eb2F2U_73ytmJqYmff2aPqL7Y_r867-A/formResponse"

# [Остальной код без изменений до этого места]

# Функция для отправки страницы
def submit_page(form_data, session, page_history, fbzx):
    form_data["fvv"] = "1"
    form_data["draftResponse"] = "[]"
    form_data["pageHistory"] = page_history
    form_data["fbzx"] = fbzx
    
    response = session.post(FORM_SUBMIT_URL, data=form_data, headers=HEADERS)
    return response

# Основной цикл отправки
for i in range(1, 301):
    session = requests.Session()
    
    # Шаг 1: Получаем начальные параметры
    fbzx, page_history = get_form_params()
    
    # Шаг 2: Отправляем первую страницу
    page1_data = {}
    page1_data[FIELD_NAMES['age']] = random.choice(AGES)
    page1_data[FIELD_NAMES['city']] = random.choice(CITIES)
    page1_data[FIELD_NAMES['frequency']] = random.choice(FREQUENCIES)
    
    # Сервисы
    selected_services = random_multi(SERVICES, 1, 3)
    for service in selected_services:
        # Для чекбоксов используем один ключ с разными значениями
        if FIELD_NAMES['services'] in page1_data:
            page1_data[FIELD_NAMES['services']] += f",{service}"
        else:
            page1_data[FIELD_NAMES['services']] = service
    
    response1 = submit_page(page1_data, session, page_history, fbzx)
    
    # Шаг 3: Извлекаем параметры для второй страницы
    if response1.status_code == 200:
        soup = BeautifulSoup(response1.text, 'html.parser')
        new_fbzx = soup.find('input', {'name': 'fbzx'}).get('value', '')
        new_page_history = "0,1"  # После первой страницы
        
        # Шаг 4: Отправляем вторую страницу
        page2_data = {}
        
        # Приоритеты
        for priority_field in FIELD_NAMES['priorities']:
            page2_data[priority_field] = str(random.randint(1, 5))
        
        # [Остальные поля второй страницы без изменений]
        
        # Для полей с множественным выбором
        for field in ['good_assortment', 'usage_situations', 'problems']:
            options = random_multi(eval(f"{field.upper()}_OPTIONS"), 1, 4)
            page2_data[FIELD_NAMES[field]] = ",".join(options)
        
        response2 = submit_page(page2_data, session, new_page_history, new_fbzx)
        
        # Проверяем статус второй страницы
        if response2.status_code == 200:
            status = "УСПЕШНО"
            success_count += 1
        else:
            status = f"ОШИБКА ({response2.status_code})"
            fail_count += 1
    else:
        status = f"ОШИБКА ПЕРВОЙ СТРАНИЦЫ ({response1.status_code})"
        fail_count += 1
    
    # [Остальная часть кода без изменений]