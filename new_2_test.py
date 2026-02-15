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
    
    # Приоритеты (10 полей)
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
SERVICES = ["Яндекс Еда", "Самокат", "Яндекс Лавка", "ВкусВилл", 
            "Заказываю напрямую из ресторанов/кафе", "Другое"]
PRICE_OPTIONS = ["0-200 р.", "200-400 р.", "400-600 р.", "600-1000 р.", "Не имеет значения"]
YES_NO = ["Да", "Нет"]
ASSORTMENT_OPTIONS = [
    "Разнообразие ресторанов/кафе/магазинов",
    "Наличие эксклюзивных товаров, которых нет у конкурентов",
    "Регулярное обновление доступных для заказа ресторанов/кафе/магазинов",
    "Широкий выбор товаров разных ценовых категорий",
    "Товары, адаптированные под разные пищевые (и не только) предпочтения",
    "Возможность выбора из ситуативных подборок (болезнь, путешествие и др)"
]
USAGE_OPTIONS = [
    "Для регулярного питания", 
    "Когда хочу расслабиться и съесть что-то вкусное", 
    "В компании или для различных мероприятий", 
    "Когда нет времени на готовку",
    "Когда хочу попробовать что-то новое или необычное", 
    "В экстренных ситуациях, когда срочно нужна еда", 
    "В путешествиях",
    "Поздний вечер/ночь", 
    "Болезнь/плохое самочувствие"
]
PROBLEMS_OPTIONS = [
    "Сложный интерфейс", 
    "Высокая стоимость доставки", 
    "Нет нужных ресторанов/блюд",
    "Задержки доставки", 
    "Узкий ассортимент", 
    "Не доставляют в нужное место",
    "Не удовлетворяет качество еды", 
    "Отсутствие рекомендаций и нужных подборок"
]
AGREE_OPTIONS = ["Да", "Нет", "Затрудняюсь ответить"]
FREQUENCY_OPTIONS = ["Постоянно", "Иногда", "Редко"]
BOXES_OPTIONS = ["Точно да", "Сомневаюсь, скорее да", "Сомневаюсь, скорее нет", "Точно нет"]
PICKUP_OPTIONS = ["Положительно", "Отрицательно"]
GROUP_ORDER_OPTIONS = ["Часто", "Иногда", "Редко"]
FAIR_PRICE_OPTIONS = ["Полностью справедлива", "Дороговато, но терпимо", "Слишком дорого"]
SUBSCRIPTION_OPTIONS = ["Куплю, если цена адекватна", "Не готов платить за подписку", "Зависит от условий"]
DELIVERY_IMPORTANCE = ["Критически важен", "Не важен", "Хочу видеть примерный интервал"]
MEDICINE_IMPORTANCE = ["Очень важно", "Не важно"]
ABROAD_IMPORTANCE = ["Очень важно", "Не важно"]
MULTIPLE_RESTAURANTS = ["Да", "Нет", "Всё равно"]
FAVORITES_BLOCK = ["Да", "Нет", "Всё равно"]

# Генераторы ответов
def random_multi(options, min_ch=1, max_ch=None):
    if max_ch is None:
        max_ch = len(options)
    n = random.randint(min_ch, min(max_ch, len(options)))
    return random.sample(options, n)

def random_text(min_words=3, max_words=15):
    words = ["доставка", "еда", "сервис", "приложение", "интерфейс", "ресторан", "продукты", "заказ",
             "вкусно", "быстро", "удобно", "качество", "цена", "ассортимент", "рекомендации", "поиск",
             "улучшить", "ускорение", "разнообразие", "скидки", "акции", "бонусы", "навигация"]
    return ' '.join(random.choices(words, k=random.randint(min_words, max_words)))

# Функция для получения актуальных параметров формы
def get_form_params():
    try:
        response = requests.get(FORM_VIEW_URL, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Извлекаем технические параметры
        fbzx = soup.find('input', {'name': 'fbzx'}).get('value', '')
        page_history = soup.find('input', {'name': 'pageHistory'}).get('value', '0,1')
        
        return fbzx, page_history
    except Exception as e:
        print(f"Ошибка при получении параметров формы: {str(e)}")
        return "-7446534891210601816", "0,1"

# Заголовки запроса
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': FORM_VIEW_URL,
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Статистика отправки
success_count = 0
fail_count = 0
failed_responses = []

print("Начало отправки ответов...")
print("-" * 50)

# Получаем актуальные параметры перед началом
FBZX, PAGE_HISTORY = get_form_params()
print(f"Используемые параметры: fbzx={FBZX}, pageHistory={PAGE_HISTORY}")

# Отправка 300 ответов
for i in range(1, 301):
    # Получаем актуальные параметры для каждой попытки
    current_fbzx, current_page_history = get_form_params()
    
    form_payload = []
    
    # Страница 1
    form_payload.append((FIELD_NAMES['age'], random.choice(AGES)))
    form_payload.append((FIELD_NAMES['city'], random.choice(CITIES)))
    form_payload.append((FIELD_NAMES['frequency'], random.choice(FREQUENCIES)))
    
    # Сервисы (несколько вариантов)
    selected_services = random_multi(SERVICES, 1, 3)
    for service in selected_services:
        form_payload.append((FIELD_NAMES['services'], service))
    
    # Другое (только если выбрана опция "Другое")
    if "Другое" in selected_services:
        form_payload.append((FIELD_NAMES['other_service'], random_text(2, 5)))
    
    # Страница 2
    # Приоритеты (1-5 для каждого пункта)
    for priority_field in FIELD_NAMES['priorities']:
        form_payload.append((priority_field, str(random.randint(1, 5))))
    
    form_payload.append((FIELD_NAMES['acceptable_price'], random.choice(PRICE_OPTIONS)))
    form_payload.append((FIELD_NAMES['refused_due_to_price'], random.choice(YES_NO)))
    
    # Хороший ассортимент (несколько вариантов)
    for option in random_multi(ASSORTMENT_OPTIONS, 1, 3):
        form_payload.append((FIELD_NAMES['good_assortment'], option))
    
    # Ситуации использования (несколько вариантов)
    for option in random_multi(USAGE_OPTIONS, 1, 4):
        form_payload.append((FIELD_NAMES['usage_situations'], option))
    
    # Проблемы (несколько вариантов)
    for option in random_multi(PROBLEMS_OPTIONS, 1, 3):
        form_payload.append((FIELD_NAMES['problems'], option))
    
    # Остальные поля
    form_payload.append((FIELD_NAMES['fair_price'], random.choice(FAIR_PRICE_OPTIONS)))
    form_payload.append((FIELD_NAMES['use_bonuses'], random.choice(YES_NO)))
    form_payload.append((FIELD_NAMES['agree_statement'], random.choice(AGREE_OPTIONS)))
    form_payload.append((FIELD_NAMES['interface_rating'], str(random.randint(1, 5))))
    form_payload.append((FIELD_NAMES['difficult_find'], random.choice(YES_NO)))
    form_payload.append((FIELD_NAMES['favorites_block'], random.choice(FAVORITES_BLOCK)))
    form_payload.append((FIELD_NAMES['annoying_elements'], random_text(5, 20)))
    form_payload.append((FIELD_NAMES['subscription_attitude'], random.choice(SUBSCRIPTION_OPTIONS)))
    form_payload.append((FIELD_NAMES['delivery_time_importance'], random.choice(DELIVERY_IMPORTANCE)))
    form_payload.append((FIELD_NAMES['preorder_pickup'], random.choice(YES_NO)))
    form_payload.append((FIELD_NAMES['combo_sets'], random.choice(AGREE_OPTIONS)))
    form_payload.append((FIELD_NAMES['same_dishes_frequency'], random.choice(FREQUENCY_OPTIONS)))
    form_payload.append((FIELD_NAMES['multiple_restaurants'], random.choice(MULTIPLE_RESTAURANTS)))
    form_payload.append((FIELD_NAMES['medicine_delivery_importance'], random.choice(MEDICINE_IMPORTANCE)))
    form_payload.append((FIELD_NAMES['medicine_piece_by_piece'], random.choice(AGREE_OPTIONS)))
    form_payload.append((FIELD_NAMES['useful_boxes'], random.choice(BOXES_OPTIONS)))
    form_payload.append((FIELD_NAMES['medicine_via_yandex'], random.choice(BOXES_OPTIONS)))
    form_payload.append((FIELD_NAMES['payment_abroad'], random.choice(ABROAD_IMPORTANCE)))
    form_payload.append((FIELD_NAMES['pickup_points_attitude'], random.choice(PICKUP_OPTIONS)))
    form_payload.append((FIELD_NAMES['group_orders_frequency'], random.choice(GROUP_ORDER_OPTIONS)))
    form_payload.append((FIELD_NAMES['multiple_restaurants_feature'], random.choice(["Да", "Нет"])))
    form_payload.append((FIELD_NAMES['improvements'], random_text(10, 25)))
    
    # Технические параметры (используем актуальные значения)
    form_payload.append(("fvv", "1"))
    form_payload.append(("draftResponse", f'[null,null,"{current_fbzx}"]'))
    form_payload.append(("pageHistory", current_page_history))
    form_payload.append(("fbzx", current_fbzx))

    try:
        response = requests.post(FORM_SUBMIT_URL, data=form_payload, headers=HEADERS)
        if response.status_code == 200:
            status = "УСПЕШНО"
            success_count += 1
        else:
            status = f"ОШИБКА ({response.status_code})"
            fail_count += 1
            failed_responses.append((i, response.status_code, response.text))
            
        # Цветное оформление статуса
        if "УСПЕШНО" in status:
            status_msg = f"\033[92m{status}\033[0m"  # Зеленый
        else:
            status_msg = f"\033[91m{status}\033[0m"  # Красный
            
        print(f"Попытка {i:03d}/300: {status_msg}")
        
    except Exception as e:
        fail_count += 1
        status_msg = f"\033[91mОШИБКА: {str(e)}\033[0m"
        print(f"Попытка {i:03d}/300: {status_msg}")
        failed_responses.append((i, "Exception", str(e)))
    
    # Случайная задержка
    delay = random.uniform(2.0, 5.0)
    time.sleep(delay)

# Итоговая статистика
print("\n" + "=" * 50)
print(f"ОТЧЕТ О ВЫПОЛНЕНИИ")
print("=" * 50)
print(f"Всего попыток: {success_count + fail_count}")
print(f"Успешных отправок: \033[92m{success_count}\033[0m")
print(f"Неудачных отправок: \033[91m{fail_count}\033[0m")
print(f"Процент успеха: {success_count/(success_count + fail_count)*100:.1f}%")

if fail_count > 0:
    print("\n" + "-" * 50)
    print("ДЕТАЛИ НЕУДАЧНЫХ ПОПЫТОК:")
    for attempt, code, error in failed_responses:
        print(f"\nПопытка #{attempt}:")
        print(f"Код ошибки: {code}")
        if len(error) > 200:
            print(f"Сообщение: {error[:200]}...")
        else:
            print(f"Сообщение: {error}")

print("\nРабота завершена!")