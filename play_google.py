# import requests
# import random
# import time
# from bs4 import BeautifulSoup

# # URL формы
# FORM_VIEW_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfrC4RB0I6-qqHwL0Eb2F2U_73ytmJqYmff2aPqL7Y_r867-A/viewform"
# FORM_SUBMIT_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfrC4RB0I6-qqHwL0Eb2F2U_73ytmJqYmff2aPqL7Y_r867-A/formResponse"

# # Идентификаторы полей
# FIELD_NAMES = {
#     "age": "entry.957985860",
#     "city": "entry.2030226639",
#     "frequency": "entry.1906260792",
#     "services": "entry.105929970",
#     "other_service": "entry.2078399687",
    
#     # Страница 2
#     "priorities": [
#         "entry.1712559987", "entry.1186777191", "entry.1845303113",
#         "entry.1379581942", "entry.907665513", "entry.175979449",
#         "entry.2067862537", "entry.1030575565", "entry.1837959956",
#         "entry.655224750"
#     ],
#     "acceptable_price": "entry.374716556",
#     "refused_due_to_price": "entry.1869701364",
#     "good_assortment": "entry.2000130975",
#     "usage_situations": "entry.1249290705",
#     "problems": "entry.489316951",
#     "fair_price": "entry.97748358",
#     "use_bonuses": "entry.21869573",
#     "agree_statement": "entry.1717533694",
#     "interface_rating": "entry.1474558508",
#     "difficult_find": "entry.93005912",
#     "favorites_block": "entry.900694445",
#     "annoying_elements": "entry.871282396",
#     "subscription_attitude": "entry.1055215167",
#     "delivery_time_importance": "entry.1792421678",
#     "preorder_pickup": "entry.1037469077",
#     "combo_sets": "entry.946368114",
#     "same_dishes_frequency": "entry.1485680832",
#     "multiple_restaurants": "entry.675161404",
#     "medicine_delivery_importance": "entry.1961163093",
#     "medicine_piece_by_piece": "entry.812039976",
#     "useful_boxes": "entry.979452090",
#     "medicine_via_yandex": "entry.418140381",
#     "payment_abroad": "entry.210872912",
#     "sim_card_order": "entry.2089454455",
#     "pickup_points_attitude": "entry.134166581",
#     "group_orders_frequency": "entry.540535588",
#     "multiple_restaurants_feature": "entry.532695062",
#     "improvements": "entry.1503052529"
# }

# # Варианты ответов
# AGES = ["До 18", "18-24", "25-34", "35-44", "45+"]
# CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", 
#           "Нижний Новгород", "Челябинск", "Самара", "Омск", "Ростов-на-Дону"]
# FREQUENCIES = ["Ежедневно", "Несколько раз в неделю", "Несколько раз в месяц", 
#                "Реже, чем раз в месяц", "Пока не заказывал(а), но имею представление, о чем речь"]
# SERVICES = ["Яндекс Еда", "Самокат", "Яндекс Лавка", "ВкусВилл", "Заказываю напрямую из ресторанов/кафе"]
# PRICE_OPTIONS = ["0-200 р.", "200-400 р.", "400-600 р.", "600-1000 р.", "Не имеет значения"]
# YES_NO = ["Да", "Нет"]
# ASSORTMENT_OPTIONS = ["Разнообразие ресторанов/кафе/магазинов", "Наличие эксклюзивных товаров, которых нет у конкурентов",
#                      "Регулярное обновление доступных для заказа ресторанов/кафе/магазинов",
#                      "Широкий выбор товаров разных ценовых категорий",
#                      "Товары, адаптированные под разные пищевые (и не только) предпочтения",
#                      "Возможность выбора из ситуативных подборок (болезнь, путешествие и др)"]
# USAGE_OPTIONS = ["Для регулярного питания", "Когда хочу расслабиться и съесть что-то вкусное", 
#                 "В компании или для различных мероприятий", "Когда нет времени на готовку",
#                 "Когда хочу попробовать что-то новое или необычное", 
#                 "В экстренных ситуациях, когда срочно нужна еда", "В путешествиях",
#                 "Поздний вечер/ночь", "Болезнь/плохое самочувствие"]
# PROBLEMS_OPTIONS = ["Сложный интерфейс", "Высокая стоимость доставки", "Нет нужных ресторанов/блюд",
#                    "Задержки доставки", "Узкий ассортимент", "Не доставляют в нужное место",
#                    "Не удовлетворяет качество еды", "Отсутствие рекомендаций и нужных подборок"]
# AGREE_OPTIONS = ["Да", "Нет", "Затрудняюсь ответить"]
# FREQUENCY_OPTIONS = ["Постоянно", "Иногда", "Редко"]
# BOXES_OPTIONS = ["Точно да", "Сомневаюсь, скорее да", "Сомневаюсь, скорее нет", "Точно нет"]
# ABROAD_OPTIONS = ["Точно да", "Сомневаюсь, скорее да", "Сомневаюсь, скорее нет", "Точно нет"]
# PICKUP_OPTIONS = ["Положительно", "Отрицательно"]
# GROUP_ORDER_OPTIONS = ["Часто", "Иногда", "Редко"]

# # Генераторы ответов
# def random_multi(options, min_ch=1, max_ch=None):
#     if max_ch is None:
#         max_ch = len(options)
#     n = random.randint(min_ch, min(max_ch, len(options)))
#     return random.sample(options, n)

# def random_text(min_words=3, max_words=15):
#     words = ["доставка", "еда", "сервис", "приложение", "интерфейс", "ресторан", "продукты", "заказ",
#              "вкусно", "быстро", "удобно", "качество", "цена", "ассортимент", "рекомендации", "поиск"]
#     return ' '.join(random.choices(words, k=random.randint(min_words, max_words)))

# # Список User-Agent для ротации
# USER_AGENTS = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
#     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
# ]

# # Функция для получения актуальных параметров формы
# def get_form_params():
#     try:
#         headers = {'User-Agent': random.choice(USER_AGENTS)}
#         response = requests.get(FORM_VIEW_URL, headers=headers, timeout=15)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Извлекаем ВСЕ скрытые поля
#         hidden_fields = {
#             inp['name']: inp.get('value', '')
#             for inp in soup.select('input[type="hidden"]')
#             if inp.has_attr('name')
#         }
        
#         # Проверка обязательных полей
#         required_fields = ['fbzx', 'pageHistory']
#         for field in required_fields:
#             if field not in hidden_fields:
#                 print(f"⚠️ Отсутствует обязательное поле: {field}")
#                 # Генерируем случайное значение, если поле отсутствует
#                 hidden_fields[field] = f"-{random.randint(10**18, 10**19-1)}" if field == 'fbzx' else "0,1"
        
#         # Добавляем обязательные поля, которые могут отсутствовать
#         if 'draftResponse' not in hidden_fields:
#             hidden_fields['draftResponse'] = "[]"
#         if 'fvv' not in hidden_fields:
#             hidden_fields['fvv'] = "1"
        
#         return hidden_fields
        
#     except Exception as e:
#         print(f"Ошибка при получении параметров: {e}")
#         # Возвращаем значения по умолчанию
#         return {
#             'fbzx': f"-{random.randint(10**18, 10**19-1)}",
#             'pageHistory': "0,1",
#             'fvv': "1",
#             'draftResponse': "[]"
#         }
# # Статистика отправки
# success_count = 0
# fail_count = 0
# failed_responses = []

# print("Начало отправки ответов...")
# print("-" * 50)

# # Отправка 300 ответов
# for i in range(1, 301):
#     # Получаем новые параметры перед каждой отправкой
#     FBZX, PAGE_HISTORY = get_form_params()
    
#     # Для полей с множественным выбором используем список кортежей
#     form_payload = []
    
#     # Страница 1
#     form_payload.append((FIELD_NAMES['age'], random.choice(AGES)))
#     form_payload.append((FIELD_NAMES['city'], random.choice(CITIES)))
#     form_payload.append((FIELD_NAMES['frequency'], random.choice(FREQUENCIES)))
    
#     # Сервисы (несколько вариантов) - ОДИН ключ, несколько значений
#     selected_services = random_multi(SERVICES, 1, 3)
#     for service in selected_services:
#         form_payload.append((FIELD_NAMES['services'], service))
    
#     # Если выбран вариант "Заказываю напрямую", заполняем поле "Другое"
#     if "Заказываю напрямую из ресторанов/кафе" in selected_services:
#         form_payload.append((FIELD_NAMES['other_service'], random_text()))
    
#     # Страница 2
#     # Приоритеты (1-10 для каждого пункта)
#     for priority_field in FIELD_NAMES['priorities']:
#         form_payload.append((priority_field, str(random.randint(1, 5))))
    
#     form_payload.append((FIELD_NAMES['acceptable_price'], random.choice(PRICE_OPTIONS)))
#     form_payload.append((FIELD_NAMES['refused_due_to_price'], random.choice(YES_NO)))
    
#     # Хороший ассортимент (несколько вариантов) - ОДИН ключ, несколько значений
#     for option in random_multi(ASSORTMENT_OPTIONS, 1, 3):
#         form_payload.append((FIELD_NAMES['good_assortment'], option))
    
#     # Ситуации использования (несколько вариантов) - ОДИН ключ, несколько значений
#     for option in random_multi(USAGE_OPTIONS, 1, 4):
#         form_payload.append((FIELD_NAMES['usage_situations'], option))
    
#     # Проблемы (несколько вариантов) - ОДИН ключ, несколько значений
#     for option in random_multi(PROBLEMS_OPTIONS, 1, 3):
#         form_payload.append((FIELD_NAMES['problems'], option))
    
#     # Остальные поля
#     form_payload.append((FIELD_NAMES['fair_price'], random.choice(["Полностью справедлива", "Дороговато, но терпимо", "Слишком дорого"])))
#     form_payload.append((FIELD_NAMES['use_bonuses'], random.choice(YES_NO)))
#     form_payload.append((FIELD_NAMES['agree_statement'], random.choice(AGREE_OPTIONS)))
#     form_payload.append((FIELD_NAMES['interface_rating'], str(random.randint(1, 5))))
#     form_payload.append((FIELD_NAMES['difficult_find'], random.choice(YES_NO)))
#     form_payload.append((FIELD_NAMES['favorites_block'], random.choice(YES_NO)))
#     form_payload.append((FIELD_NAMES['annoying_elements'], random_text()))
#     form_payload.append((FIELD_NAMES['subscription_attitude'], random.choice(["Куплю, если цена адекватна", "Не готов платить за подписку", "Зависит от условий"])))
#     form_payload.append((FIELD_NAMES['delivery_time_importance'], random.choice(["Критически важен", "Не важен", "Хочу видеть примерный интервал"])))
#     form_payload.append((FIELD_NAMES['preorder_pickup'], random.choice(YES_NO)))
#     form_payload.append((FIELD_NAMES['combo_sets'], random.choice(AGREE_OPTIONS)))
#     form_payload.append((FIELD_NAMES['same_dishes_frequency'], random.choice(FREQUENCY_OPTIONS)))
#     form_payload.append((FIELD_NAMES['multiple_restaurants'], random.choice(AGREE_OPTIONS)))
#     form_payload.append((FIELD_NAMES['medicine_delivery_importance'], random.choice(["Очень важно", "Не важно"])))
#     form_payload.append((FIELD_NAMES['medicine_piece_by_piece'], random.choice(YES_NO)))
#     form_payload.append((FIELD_NAMES['useful_boxes'], random.choice(BOXES_OPTIONS)))
#     form_payload.append((FIELD_NAMES['medicine_via_yandex'], random.choice(BOXES_OPTIONS)))
#     form_payload.append((FIELD_NAMES['payment_abroad'], random.choice(["Очень важно", "Не важно"])))
#     form_payload.append((FIELD_NAMES['sim_card_order'], random.choice(ABROAD_OPTIONS)))
#     form_payload.append((FIELD_NAMES['pickup_points_attitude'], random.choice(PICKUP_OPTIONS)))
#     form_payload.append((FIELD_NAMES['group_orders_frequency'], random.choice(GROUP_ORDER_OPTIONS)))
#     form_payload.append((FIELD_NAMES['multiple_restaurants_feature'], random.choice(["Да", "Нет"])))
#     form_payload.append((FIELD_NAMES['improvements'], random_text()))
    
#     # Технические параметры
#     form_payload.append(("fvv", "1"))
#     form_payload.append(("draftResponse", "[]"))
#     form_payload.append(("pageHistory", PAGE_HISTORY))
#     form_payload.append(("fbzx", FBZX))

#     # Ротация User-Agent для каждого запроса
#     headers = {
#         'User-Agent': random.choice(USER_AGENTS),
#         'Referer': FORM_VIEW_URL,
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }

#     try:
#         response = requests.post(FORM_SUBMIT_URL, data=form_payload, headers=headers, timeout=15)
#         if response.status_code == 200:
#             status = "УСПЕШНО"
#             success_count += 1
#         else:
#             status = f"ОШИБКА ({response.status_code})"
#             fail_count += 1
#             failed_responses.append((i, response.status_code, response.text))
#             print(f"\n--- Ошибка при отправке #{i} ---")
#             print(f"Статус код: {response.status_code}")
#             print("Отправленные данные:")
#             for name, value in form_payload:
#                 print(f"{name}: {value}")
            
#             print("\nОтвет сервера:")
#             print(response.text[:500])  # Первые 500 символов ответа
#             print("-" * 50)
            
#             status = f"ОШИБКА ({response.status_code})"
#             fail_count += 1
#             failed_responses.append((i, response.status_code, response.text))
            
#         # Цветное оформление статуса
#         if "УСПЕШНО" in status:
#             status_msg = f"\033[92m{status}\033[0m"  # Зеленый
#         else:
#             status_msg = f"\033[91m{status}\033[0m"  # Красный
            
#         print(f"Попытка {i:03d}/300: {status_msg}")
        
#     except Exception as e:
#         fail_count += 1
#         status_msg = f"\033[91mОШИБКА: {str(e)}\033[0m"
#         print(f"Попытка {i:03d}/300: {status_msg}")
#         failed_responses.append((i, "Exception", str(e)))
    
#     # Увеличенная случайная задержка (5-15 секунд)
#     delay = random.uniform(5.0, 15.0)
#     time.sleep(delay)

#     if "captcha" in response.text.lower():
#         print("🔥 Обнаружена CAPTCHA! Прерываем выполнение.")
#         break

# # Итоговая статистика
# print("\n" + "=" * 50)
# print(f"ОТЧЕТ О ВЫПОЛНЕНИИ")
# print("=" * 50)
# print(f"Всего попыток: {success_count + fail_count}")
# print(f"Успешных отправок: \033[92m{success_count}\033[0m")
# print(f"Неудачных отправок: \033[91m{fail_count}\033[0m")
# if success_count + fail_count > 0:
#     print(f"Процент успеха: {success_count/(success_count + fail_count)*100:.1f}%")

# if fail_count > 0:
#     print("\n" + "-" * 50)
#     print("ДЕТАЛИ НЕУДАЧНЫХ ПОПЫТОК:")
#     for attempt, code, error in failed_responses:
#         print(f"\nПопытка #{attempt}:")
#         print(f"Код ошибки: {code}")
#         if isinstance(error, str) and len(error) > 200:
#             print(f"Сообщение: {error[:200]}...")
#         else:
#             print(f"Сообщение: {error}")

# print("\nРабота завершена!")


import requests
import random
import time
from bs4 import BeautifulSoup

# URL формы
FORM_VIEW_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfrC4RB0I6-qqHwL0Eb2F2U_73ytmJqYmff2aPqL7Y_r867-A/viewform"
FORM_SUBMIT_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfrC4RB0I6-qqHwL0Eb2F2U_73ytmJqYmff2aPqL7Y_r867-A/formResponse"

# Идентификаторы полей
FIELD_NAMES = {
    "age": "entry.957985860",
    "city": "entry.2030226639",
    "frequency": "entry.1906260792",
    "services": "entry.105929970",
    "other_service": "entry.2078399687",
    
    # Страница 2
    "priorities": [
        "entry.1712559987", "entry.1186777191", "entry.1845303113",
        "entry.1379581942", "entry.907665513", "entry.175979449",
        "entry.2067862537", "entry.1030575565", "entry.1837959956",
        "entry.655224750"
    ],
    "acceptable_price": "entry.374716556",
    "refused_due_to_price": "entry.1869701364",
    "good_assortment": "entry.2000130975",
    "usage_situations": "entry.1249290705",
    "problems": "entry.489316951",
    "fair_price": "entry.97748358",
    "use_bonuses": "entry.21869573",
    "agree_statement": "entry.1717533694",
    "interface_rating": "entry.1474558508",
    "difficult_find": "entry.93005912",
    "favorites_block": "entry.900694445",
    "annoying_elements": "entry.871282396",
    "subscription_attitude": "entry.1055215167",
    "delivery_time_importance": "entry.1792421678",
    "preorder_pickup": "entry.1037469077",
    "combo_sets": "entry.946368114",
    "same_dishes_frequency": "entry.1485680832",
    "multiple_restaurants": "entry.675161404",
    "medicine_delivery_importance": "entry.1961163093",
    "medicine_piece_by_piece": "entry.812039976",
    "useful_boxes": "entry.979452090",
    "medicine_via_yandex": "entry.418140381",
    "payment_abroad": "entry.210872912",
    "sim_card_order": "entry.2089454455",
    "pickup_points_attitude": "entry.134166581",
    "group_orders_frequency": "entry.540535588",
    "multiple_restaurants_feature": "entry.532695062",
    "improvements": "entry.1503052529"
}

# Варианты ответов
AGES = ["До 18", "18-24", "25-34", "35-44", "45+"]
CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", 
          "Нижний Новгород", "Челябинск", "Самара", "Омск", "Ростов-на-Дону"]
FREQUENCIES = ["Ежедневно", "Несколько раз в неделю", "Несколько раз в месяц", 
               "Реже, чем раз в месяц", "Пока не заказывал(а), но имею представление, о чем речь"]
SERVICES = ["Яндекс Еда", "Самокат", "Яндекс Лавка", "ВкусВилл", "Заказываю напрямую из ресторанов/кафе"]
PRICE_OPTIONS = ["0-200 р.", "200-400 р.", "400-600 р.", "600-1000 р.", "Не имеет значения"]
YES_NO = ["Да", "Нет"]
ASSORTMENT_OPTIONS = ["Разнообразие ресторанов/кафе/магазинов", "Наличие эксклюзивных товаров, которых нет у конкурентов",
                     "Регулярное обновление доступных для заказа ресторанов/кафе/магазинов",
                     "Широкий выбор товаров разных ценовых категорий",
                     "Товары, адаптированные под разные пищевые (и не только) предпочтения",
                     "Возможность выбора из ситуативных подборок (болезнь, путешествие и др)"]
USAGE_OPTIONS = ["Для регулярного питания", "Когда хочу расслабиться и съесть что-то вкусное", 
                "В компании или для различных мероприятий", "Когда нет времени на готовку",
                "Когда хочу попробовать что-то новое или необычное", 
                "В экстренных ситуациях, когда срочно нужна еда", "В путешествиях",
                "Поздний вечер/ночь", "Болезнь/плохое самочувствие"]
PROBLEMS_OPTIONS = ["Сложный интерфейс", "Высокая стоимость доставки", "Нет нужных ресторанов/блюд",
                   "Задержки доставки", "Узкий ассортимент", "Не доставляют в нужное место",
                   "Не удовлетворяет качество еды", "Отсутствие рекомендаций и нужных подборок"]
AGREE_OPTIONS = ["Да", "Нет", "Затрудняюсь ответить"]
FREQUENCY_OPTIONS = ["Постоянно", "Иногда", "Редко"]
BOXES_OPTIONS = ["Точно да", "Сомневаюсь, скорее да", "Сомневаюсь, скорее нет", "Точно нет"]
ABROAD_OPTIONS = ["Точно да", "Сомневаюсь, скорее да", "Сомневаюсь, скорее нет", "Точно нет"]
PICKUP_OPTIONS = ["Положительно", "Отрицательно"]
GROUP_ORDER_OPTIONS = ["Часто", "Иногда", "Редко"]

# Список User-Agent
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1'
]

def get_form_params():
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(FORM_VIEW_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Извлекаем ВСЕ скрытые поля
        hidden_fields = {
            inp['name']: inp.get('value', '')
            for inp in soup.select('input[type="hidden"]')
            if inp.has_attr('name')
        }
        
        # Проверка обязательных полей
        required_fields = ['fbzx', 'pageHistory']
        for field in required_fields:
            if field not in hidden_fields:
                print(f"⚠️ Отсутствует обязательное поле: {field}")
                # Генерируем случайное значение, если поле отсутствует
                hidden_fields[field] = f"-{random.randint(10**18, 10**19-1)}" if field == 'fbzx' else "0,1"
        
        # Добавляем обязательные поля, которые могут отсутствовать
        if 'draftResponse' not in hidden_fields:
            hidden_fields['draftResponse'] = "[]"
        if 'fvv' not in hidden_fields:
            hidden_fields['fvv'] = "1"
        
        return hidden_fields
        
    except Exception as e:
        print(f"Ошибка при получении параметров: {e}")
        # Возвращаем значения по умолчанию
        return {
            'fbzx': f"-{random.randint(10**18, 10**19-1)}",
            'pageHistory': "0,1",
            'fvv': "1",
            'draftResponse': "[]"
        }
# Генераторы ответов
def random_multi(options, min_ch=1, max_ch=None):
    if max_ch is None:
        max_ch = len(options)
    n = random.randint(min_ch, min(max_ch, len(options)))
    return random.sample(options, n)

def random_text(min_words=3, max_words=15):
    words = ["доставка", "еда", "сервис", "приложение", "интерфейс", "ресторан", "продукты", "заказ",
             "вкусно", "быстро", "удобно", "качество", "цена", "ассортимент", "рекомендации", "поиск"]
    return ' '.join(random.choices(words, k=random.randint(min_words, max_words)))


# Статистика
success_count = 0
fail_count = 0
failed_responses = []

print("Начало отправки ответов с улучшенной обработкой...")
print("-" * 50)

for i in range(1, 301):
    try:
        # Получаем параметры формы
        hidden_params = get_form_params()
        
        # Формируем payload
        form_payload = []
        
        # 1. Сначала добавляем ВСЕ скрытые поля
        for name, value in hidden_params.items():
            form_payload.append((name, value))
        
        # Страница 1
        form_payload.append((FIELD_NAMES['age'], random.choice(AGES)))
        form_payload.append((FIELD_NAMES['city'], random.choice(CITIES)))
        form_payload.append((FIELD_NAMES['frequency'], random.choice(FREQUENCIES)))
        
        # Сервисы (несколько вариантов) - ОДИН ключ, несколько значений
        selected_services = random_multi(SERVICES, 1, 3)
        for service in selected_services:
            form_payload.append((FIELD_NAMES['services'], service))
        
        # Если выбран вариант "Заказываю напрямую", заполняем поле "Другое"
        if "Заказываю напрямую из ресторанов/кафе" in selected_services:
            form_payload.append((FIELD_NAMES['other_service'], random_text()))
        
        # Страница 2
        # Приоритеты (1-10 для каждого пункта)
        for priority_field in FIELD_NAMES['priorities']:
            form_payload.append((priority_field, str(random.randint(1, 5))))
        
        form_payload.append((FIELD_NAMES['acceptable_price'], random.choice(PRICE_OPTIONS)))
        form_payload.append((FIELD_NAMES['refused_due_to_price'], random.choice(YES_NO)))
        
        # Хороший ассортимент (несколько вариантов) - ОДИН ключ, несколько значений
        for option in random_multi(ASSORTMENT_OPTIONS, 1, 3):
            form_payload.append((FIELD_NAMES['good_assortment'], option))
        
        # Ситуации использования (несколько вариантов) - ОДИН ключ, несколько значений
        for option in random_multi(USAGE_OPTIONS, 1, 4):
            form_payload.append((FIELD_NAMES['usage_situations'], option))
        
        # Проблемы (несколько вариантов) - ОДИН ключ, несколько значений
        for option in random_multi(PROBLEMS_OPTIONS, 1, 3):
            form_payload.append((FIELD_NAMES['problems'], option))
        
        # Остальные поля
        form_payload.append((FIELD_NAMES['fair_price'], random.choice(["Полностью справедлива", "Дороговато, но терпимо", "Слишком дорого"])))
        form_payload.append((FIELD_NAMES['use_bonuses'], random.choice(YES_NO)))
        form_payload.append((FIELD_NAMES['agree_statement'], random.choice(AGREE_OPTIONS)))
        form_payload.append((FIELD_NAMES['interface_rating'], str(random.randint(1, 5))))
        form_payload.append((FIELD_NAMES['difficult_find'], random.choice(YES_NO)))
        form_payload.append((FIELD_NAMES['favorites_block'], random.choice(YES_NO)))
        form_payload.append((FIELD_NAMES['annoying_elements'], random_text()))
        form_payload.append((FIELD_NAMES['subscription_attitude'], random.choice(["Куплю, если цена адекватна", "Не готов платить за подписку", "Зависит от условий"])))
        form_payload.append((FIELD_NAMES['delivery_time_importance'], random.choice(["Критически важен", "Не важен", "Хочу видеть примерный интервал"])))
        form_payload.append((FIELD_NAMES['preorder_pickup'], random.choice(YES_NO)))
        form_payload.append((FIELD_NAMES['combo_sets'], random.choice(AGREE_OPTIONS)))
        form_payload.append((FIELD_NAMES['same_dishes_frequency'], random.choice(FREQUENCY_OPTIONS)))
        form_payload.append((FIELD_NAMES['multiple_restaurants'], random.choice(AGREE_OPTIONS)))
        form_payload.append((FIELD_NAMES['medicine_delivery_importance'], random.choice(["Очень важно", "Не важно"])))
        form_payload.append((FIELD_NAMES['medicine_piece_by_piece'], random.choice(YES_NO)))
        form_payload.append((FIELD_NAMES['useful_boxes'], random.choice(BOXES_OPTIONS)))
        form_payload.append((FIELD_NAMES['medicine_via_yandex'], random.choice(BOXES_OPTIONS)))
        form_payload.append((FIELD_NAMES['payment_abroad'], random.choice(["Очень важно", "Не важно"])))
        form_payload.append((FIELD_NAMES['sim_card_order'], random.choice(ABROAD_OPTIONS)))
        form_payload.append((FIELD_NAMES['pickup_points_attitude'], random.choice(PICKUP_OPTIONS)))
        form_payload.append((FIELD_NAMES['group_orders_frequency'], random.choice(GROUP_ORDER_OPTIONS)))
        form_payload.append((FIELD_NAMES['multiple_restaurants_feature'], random.choice(["Да", "Нет"])))
        form_payload.append((FIELD_NAMES['improvements'], random_text()))
        
        # Ротация User-Agent
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Referer': FORM_VIEW_URL,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Отправка
        response = requests.post(
            FORM_SUBMIT_URL,
            data=form_payload,
            headers=headers,
            timeout=20
        )
        
        # Обработка ответа
        if response.status_code == 200:
            status = "УСПЕШНО"
            success_count += 1
            status_msg = f"\033[92m{status}\033[0m"
        else:
            status = f"ОШИБКА ({response.status_code})"
            fail_count += 1
            failed_responses.append((i, response.status_code, response.text))
            status_msg = f"\033[91m{status}\033[0m"
            
            # Детальное логирование ошибки
            print(f"\n--- Ошибка #{i} ---")
            print(f"Статус: {response.status_code}")
            print("Отправленные данные:")
            for name, value in form_payload:
                print(f"{name}: {value}")
            print("\nОтвет сервера:")
            print(response.text[:1000])  # Первые 1000 символов
            print("-" * 50)
        
        print(f"Попытка {i:03d}/300: {status_msg}")
        
        # Проверка на капчу
        if "captcha" in response.text.lower():
            print("🔥 Обнаружена CAPTCHA! Прерываем выполнение.")
            break
            
    except Exception as e:
        fail_count += 1
        error_msg = str(e)
        print(f"Попытка {i:03d}/300: \033[91mОШИБКА: {error_msg}\033[0m")
        failed_responses.append((i, "Exception", error_msg))
        
        # Для сетевых ошибок - пауза подольше
        if "connection" in error_msg.lower():
            time.sleep(30)
    
    # Увеличенная задержка
    delay = random.uniform(15.0, 30.0)
    time.sleep(delay)

# Вывод статистики
print("\n" + "=" * 50)
print(f"ОТЧЕТ О ВЫПОЛНЕНИИ")
print("=" * 50)
print(f"Всего попыток: {success_count + fail_count}")
print(f"Успешных отправок: \033[92m{success_count}\033[0m")
print(f"Неудачных отправок: \033[91m{fail_count}\033[0m")
if success_count + fail_count > 0:
    print(f"Процент успеха: {success_count/(success_count + fail_count)*100:.1f}%")

if fail_count > 0:
    print("\n" + "-" * 50)
    print("ДЕТАЛИ НЕУДАЧНЫХ ПОПЫТОК:")
    for attempt, code, error in failed_responses:
        print(f"\nПопытка #{attempt}:")
        print(f"Код ошибки: {code}")
        if isinstance(error, str) and len(error) > 200:
            print(f"Сообщение: {error[:200]}...")
        else:
            print(f"Сообщение: {error}")

print("\nРабота завершена!")