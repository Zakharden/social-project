import requests
import random
import time
from urllib.parse import urlencode

# Функции для генерации ответов
def get_random_age():
    return random.choice(["До 18", "18-24", "25-34", "35-44", "45+"])

def get_random_city():
    cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", "Сочи", "Калининград"]
    return random.choice(cities)

def get_random_frequency():
    return random.choice([
        "Ежедневно",
        "Несколько раз в неделю",
        "Несколько раз в месяц",
        "Реже, чем раз в месяц",
        "Пока не заказывал(а), но имею представление, о чем речь"
    ])

def get_random_services():
    services = [
        "Яндекс Еда", 
        "Самокат", 
        "Яндекс Лавка", 
        "ВкусВилл", 
        "Заказываю напрямую из ресторанов/кафе",
        "Другое"
    ]
    selected = random.sample(services, random.randint(1, 3))
    other_text = ""
    if "Другое" in selected:
        other_text = random.choice(["Delivery Club", "Ozon", "SberMarket", "Wildberries"])
    return selected, other_text

def get_priority_rating():
    return str(random.randint(1, 5))

def get_acceptable_price():
    return random.choice(["0-200 р.", "200-400 р.", "400-600 р.", "600-1000 р.", "Не имеет значения"])

def get_random_assortment():
    options = [
        "Разнообразие ресторанов/кафе/магазинов",
        "Наличие эксклюзивных товаров, которых нет у конкурентов",
        "Регулярное обновление доступных для заказа ресторанов/кафе/магазинов",
        "Широкий выбор товаров разных ценовых категорий",
        "Товары, адаптированные под разные пищевые (и не только) предпочтения",
        "Возможность выбора из ситуативных подборок (болезнь, путешествие и др)"
    ]
    return random.sample(options, random.randint(2, 4))

def get_usage_scenarios():
    scenarios = [
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
    return random.sample(scenarios, random.randint(3, 5))

def get_random_problems():
    problems = [
        "Сложный интерфейс",
        "Высокая стоимость доставки",
        "Нет нужных ресторанов/блюд",
        "Задержки доставки",
        "Узкий ассортимент",
        "Не доставляют в нужное место",
        "Не удовлетворяет качество еды",
        "Отсутствие рекомендаций и нужных подборок"
    ]
    return random.sample(problems, random.randint(1, 3))

def get_annoying_elements():
    elements = [
        "Навязчивая реклама",
        "Слишком частые уведомления",
        "Сложная навигация",
        "Медленная загрузка",
        "Требует много разрешений",
        "Слишком много шагов для заказа",
        "Неудобный поиск",
        "Проблемы с корзиной"
    ]
    return random.choice(elements)

def get_fairness():
    return random.choice(["Полностью справедлива", "Дороговато, но терпимо", "Слишком дорого"])

def get_yes_no():
    return random.choice(["Да", "Нет"])

def get_rating():
    return str(random.randint(1, 5))

def get_difficulty():
    return random.choice(["Да", "Нет"])

def get_wish_block():
    return random.choice(["Да", "Нет", "Всё равно"])

def get_subscription():
    return random.choice(["Куплю, если цена адекватна", "Не готов платить за подписку", "Зависит от условий"])

def get_delivery_time():
    return random.choice(["Критически важен", "Не важен", "Хочу видеть примерный интервал"])

def get_yes_no_unsure():
    return random.choice(["Да", "Нет", "Затрудняюсь ответить"])

def get_order_frequency():
    return random.choice(["Постоянно", "Иногда", "Редко"])

def get_importance():
    return random.choice(["Очень важно", "Не важно"])

def get_box_interest():
    return random.choice(["Точно да", "Сомневаюсь, скорее да", "Сомневаюсь, скорее нет", "Точно нет"])

def get_meds_interest():
    return random.choice(["Точно да", "Сомневаюсь, скорее да", "Сомневаюсь, скорее нет", "Точно нет"])

def get_attitude():
    return random.choice(["Положительно", "Отрицательно"])

def get_group_order_frequency():
    return random.choice(["Часто", "Иногда", "Редко"])

def get_improvements():
    suggestions = [
        "Улучшить систему рекомендаций",
        "Добавить фильтры по диетическим ограничениям",
        "Уменьшить стоимость доставки",
        "Увеличить зону покрытия",
        "Улучшить качество упаковки",
        "Добавить возможность предзаказа",
        "Упростить интерфейс",
        "Расширить ассортимент ресторанов",
        "Улучшить систему поиска блюд",
        "Предоставлять больше информации о составе блюд"
    ]
    return random.choice(suggestions)

# ID формы
FORM_ID = "1TYpagtYV2l9e-eS-HVGlBV-LOYOLjMlqDgg1dvLiqkk"
SUBMIT_URL = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"

def generate_payload():
    """Генерирует payload в формате, который ожидает Google Forms"""
    # Создаем список ответов в формате [null, null, [ответ], ...]
    responses = []
    
    # Ваш возраст
    responses.append([None, None, [get_random_age()]])
    
    # В каком городе вы живете?
    responses.append([None, None, [get_random_city()]])
    
    # Как часто вы пользуетесь сервисами доставки еды?
    responses.append([None, None, [get_random_frequency()]])
    
    # Какими сервисами доставки вы пользуетесь чаще всего?
    services, other_text = get_random_services()
    responses.append([None, None, services])
    
    # Приоритеты (первый блок)
    for _ in range(10):
        responses.append([None, None, [get_priority_rating()]])
    
    # Приоритеты (второй блок)
    for _ in range(10):
        responses.append([None, None, [get_priority_rating()]])
    
    # Какая цена доставки является для вас приемлемой?
    responses.append([None, None, [get_acceptable_price()]])
    
    # Было ли такое, что вы отказывались от заказа?
    responses.append([None, None, [get_yes_no()]])
    
    # Что для вас означает "хороший ассортимент"?
    responses.append([None, None, get_random_assortment()])
    
    # В каких ситуациях вы обычно используете сервисы доставки?
    responses.append([None, None, get_usage_scenarios()])
    
    # Какие элементы приложения раздражают или мешают?
    responses.append([None, None, [get_annoying_elements()]])
    
    # С какими проблемами вы сталкиваетесь при заказе?
    responses.append([None, None, get_random_problems()])
    
    # Насколько справедливой вам кажется текущая стоимость доставки?
    responses.append([None, None, [get_fairness()]])
    
    # Используете ли вы бонусные баллы или кэшбэк?
    responses.append([None, None, [get_yes_no()]])
    
    # Согласны ли вы с утверждением: ...
    responses.append([None, None, [get_yes_no_unsure()]])
    
    # Оцените удобство интерфейса Яндекс Еды
    responses.append([None, None, [get_rating()]])
    
    # Сложно ли вам находить подходящие блюда?
    responses.append([None, None, [get_difficulty()]])
    
    # Хотели бы вы видеть блок с «Частыми заказами»?
    responses.append([None, None, [get_wish_block()]])
    
    # Как вы отнесетесь к подписке с фиксированной стоимостью доставки?
    responses.append([None, None, [get_subscription()]])
    
    # Насколько важен для вас выбор точного времени доставки?
    responses.append([None, None, [get_delivery_time()]])
    
    # Оформили бы вы предзаказ продуктов/блюд в постамат?
    responses.append([None, None, [get_yes_no()]])
    
    # Заказывали бы вы комбо-наборы?
    responses.append([None, None, [get_yes_no_unsure()]])
    
    # Как часто вы заказываете одни и те же блюда?
    responses.append([None, None, [get_order_frequency()]])
    
    # Хотели бы вы собирать заказ из нескольких ресторанов?
    responses.append([None, None, [get_wish_block()]])
    
    # Насколько важно для вас получать лекарства доставкой?
    responses.append([None, None, [get_importance()]])
    
    # Покупали бы вы лекарства поштучно?
    responses.append([None, None, [get_yes_no_unsure()]])
    
    # Боксы для конкретных ситуаций
    responses.append([None, None, [get_box_interest()]])
    
    # Стали бы вы пользоваться доставкой лекарств?
    responses.append([None, None, [get_meds_interest()]])
    
    # Оплата российской картой за границей
    responses.append([None, None, [get_importance()]])
    
    # Забирать заказы из точек выдачи
    responses.append([None, None, [get_attitude()]])
    
    # Групповые заказы
    responses.append([None, None, [get_group_order_frequency()]])
    
    # Разделение заказа на несколько ресторанов
    responses.append([None, None, [get_yes_no()]])
    
    # Какие улучшения вы предложили бы?
    responses.append([None, None, [get_improvements()]])
    
    # Формируем полный payload
    payload = [
        [
            "forms",
            None,
            None,
            [
                "",
                int(time.time() * 1000),  # Текущее время в миллисекундах
                int(time.time() * 1000) + 10000,  # Время + 10 секунд
                None,
                "-8096293297097394391",  # Фиксированное значение из примера
                None,
                responses
            ],
            None,
            1
        ],
        ["di", 103]  # Фиксированное значение из примера
    ]
    
    return json.dumps(payload)

# Отправка формы
def submit_form():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://docs.google.com/forms/d/e/{FORM_ID}/viewform",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://docs.google.com"
    }
    
    try:
        # Генерируем payload в правильном формате
        payload = generate_payload()
        
        # Параметры запроса
        params = {
            "authuser": "0",
            "hl": "ru",
            "rt": "j",
            "m": "!1",
            "v": "2",
            "t": str(int(time.time() * 1000))  # Текущее время в миллисекундах
        }
        
        # Тело запроса
        data = {
            "f.req": payload,
            "at": "AKV9Vz0eFjXJ4dXxZzGx5dGQ1JY9Bw:1749502989041"  # Временный токен
        }
        
        full_url = f"{SUBMIT_URL}?{urlencode(params)}"
        
        response = requests.post(full_url, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Форма успешно отправлена!")
            return True
        else:
            print(f"❌ Ошибка отправки формы: {response.status_code}")
            print(f"URL: {response.url}")
            print(f"Ответ сервера: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"🚨 Произошла ошибка: {str(e)}")
        return False

# Запуск отправки
if __name__ == "__main__":
    # Количество отправок
    submissions = 50
    success_count = 0
    
    for i in range(submissions):
        print(f"\nОтправка #{i+1} из {submissions}")
        if submit_form():
            success_count += 1
        
        # Случайная задержка между запросами
        delay = random.uniform(2.0, 5.0)
        time.sleep(delay)
    
    print(f"\nРезультат: успешно отправлено {success_count} из {submissions} форм")