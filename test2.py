import requests
import random
import time

# URL формы
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfrC4RB0I6-qqHwL0Eb2F2U_73ytmJqYmff2aPqL7Y_r867-A/formResponse"

# Идентификаторы полей
FIELD_NAMES = {
    "age": "entry.683158895",
    "city": "entry.718118116",
    "frequency": "entry.2022043250",
    "services": "entry.640083063",
    "other_service": "entry.759642210",  
    
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

# Заголовки запроса
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://docs.google.com/forms/d/e/1FAIpQLSfrC4RB0I6-qqHwL0Eb2F2U_73ytmJqYmff2aPqL7Y_r867-A/viewform',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Технические параметры
FBZX = "-7987162531628068791"
PAGE_HISTORY = "0,1"

# Статистика отправки
success_count = 0
fail_count = 0
failed_responses = []

print("Начало отправки ответов...")
print("-" * 50)

# Отправка 300 ответов
for i in range(1, 301):
    form_data = {}
    
    # Заполнение данных формы
    # [код заполнения формы без изменений]
    
    # Технические параметры
    form_data["fvv"] = "1"
    form_data["draftResponse"] = "[]"
    form_data["pageHistory"] = PAGE_HISTORY
    form_data["fbzx"] = FBZX

    try:
        response = requests.post(FORM_URL, data=form_data, headers=HEADERS)
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
    delay = random.uniform(1.5, 4.0)
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