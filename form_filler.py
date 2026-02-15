# import time
# import random
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # Настройки браузера
# chrome_options = Options()
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--disable-infobars")
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
# chrome_options.add_experimental_option('useAutomationExtension', False)

# FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfegSLrxN8kB3NHDAUg0AeCdCfxzEIqd2DONBYkyJ9G5YIacg/viewform"

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

# def human_delay(min_sec=0.5, max_sec=3.0):
#     time.sleep(random.uniform(min_sec, max_sec))

# def scroll_to_element(driver, element):
#     """Плавная прокрутка к элементу"""
#     try:
#         driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
#         human_delay(0.5, 1.0)
#     except Exception as e:
#         print(f"Ошибка при прокрутке: {str(e)}")

# def safe_click(driver, element):
#     """Безопасный клик с обработкой исключений"""
#     try:
#         scroll_to_element(driver, element)
#         human_delay(0.2, 0.5)
#         element.click()
#         return True
#     except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException) as e:
#         print(f"Элемент недоступен для клика: {str(e)}")
#         return False
#     except Exception as e:
#         print(f"Ошибка при клике: {str(e)}")
#         return False

# def select_random_option(driver, question_xpath, options):
#     """Выбирает случайный вариант ответа для вопроса"""
#     human_delay()
#     try:
#         # Получаем контейнер вопроса
#         question_container = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, question_xpath)))
#         scroll_to_element(driver, question_container)
        
#         # Получаем все варианты ответа для вопроса
#         choices = question_container.find_elements(By.XPATH, ".//div[@role='radio']")
#         if not choices:
#             choices = question_container.find_elements(By.XPATH, ".//div[@role='checkbox']")
        
#         if choices:
#             # Выбираем случайный вариант
#             random_choice = random.choice(choices)
#             return safe_click(driver, random_choice)
#         return False
#     except Exception as e:
#         print(f"Ошибка при выборе варианта: {str(e)}")
#         return False

# def select_multiple_options(driver, question_xpath, options, min_choices=1, max_choices=3):
#     """Выбирает несколько случайных вариантов (для чекбоксов)"""
#     human_delay()
#     try:
#         # Получаем контейнер вопроса
#         question_container = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, question_xpath)))
#         scroll_to_element(driver, question_container)
        
#         choices = question_container.find_elements(By.XPATH, ".//div[@role='checkbox']")
        
#         if choices:
#             # Выбираем случайное количество вариантов
#             num_choices = random.randint(min_choices, min(max_choices, len(choices)))
#             selected = random.sample(choices, num_choices)
            
#             for choice in selected:
#                 if not safe_click(driver, choice):
#                     return False
#                 human_delay(0.1, 0.5)
#             return True
#         return False
#     except Exception as e:
#         print(f"Ошибка при выборе нескольких вариантов: {str(e)}")
#         return False

# def fill_priority_questions(driver, priorities_xpath, count=10):
#     """Заполняет вопросы с приоритетами (шкала 1-5)"""
#     human_delay()
#     try:
#         # Получаем контейнер с приоритетами
#         priorities_container = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, priorities_xpath)))
#         scroll_to_element(driver, priorities_container)
        
#         # Находим все вопросы приоритетов
#         priority_questions = priorities_container.find_elements(By.XPATH, ".//div[@role='listitem']")
        
#         for i in range(min(count, len(priority_questions))):
#             question = priority_questions[i]
#             scroll_to_element(driver, question)
            
#             # Выбираем случайное значение от 1 до 5
#             value = random.randint(1, 5)
            
#             # Находим радиогруппу
#             radio_group = question.find_element(By.XPATH, ".//div[@role='radiogroup']")
            
#             # Находим соответствующую радиокнопку
#             radio = radio_group.find_element(By.XPATH, f".//div[@data-value='{value}']")
            
#             if not safe_click(driver, radio):
#                 return False
#             human_delay(0.3, 0.8)
#         return True
#     except Exception as e:
#         print(f"Ошибка при заполнении приоритетов: {str(e)}")
#         return False

# def fill_text_field(driver, question_xpath, text):
#     """Заполняет текстовое поле"""
#     human_delay()
#     try:
#         # Получаем контейнер вопроса
#         question_container = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, question_xpath)))
#         scroll_to_element(driver, question_container)
        
#         # Пытаемся найти поле ввода
#         try:
#             text_area = question_container.find_element(By.XPATH, ".//textarea")
#         except NoSuchElementException:
#             try:
#                 text_area = question_container.find_element(By.XPATH, ".//input[@type='text']")
#             except NoSuchElementException:
#                 print("❌ Не найдено текстовое поле")
#                 return False
        
#         scroll_to_element(driver, text_area)
#         human_delay(0.5, 1.0)
        
#         # Очищаем поле (если нужно) и вводим текст
#         text_area.clear()
#         for char in text:
#             text_area.send_keys(char)
#             human_delay(0.02, 0.05)  # Эмуляция печати
#         return True
#     except Exception as e:
#         print(f"❌ Ошибка при заполнении текстового поля: {str(e)}")
#         return False

# def fill_form(driver):
#     """Основная функция заполнения формы"""
#     try:
#         # Открываем форму
#         driver.get(FORM_URL)
#         print("Форма загружена")
        
#         # Ожидаем загрузки основной части формы
#         WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.XPATH, "//div[@role='listitem']")))
#         human_delay(2, 4)
        
#         # ----------------- ЗАПОЛНЕНИЕ ФОРМЫ -----------------
#         print("Заполняем форму...")
        
#         # Возраст
#         select_random_option(driver, "(//div[@role='list'])[1]", AGES)
        
#         # Город
#         select_random_option(driver, "(//div[@role='list'])[2]", CITIES)
        
#         # Частота использования
#         select_random_option(driver, "(//div[@role='list'])[3]", FREQUENCIES)
        
#         # Сервисы доставки (можно выбрать несколько)
#         select_multiple_options(driver, "(//div[@role='list'])[4]", SERVICES)
        
#         # Приоритеты (10 вопросов)
#         fill_priority_questions(driver, "//div[@role='group' and contains(@class, 'm6QOd')]", 10)
        
#         # Приемлемая цена доставки
#         select_random_option(driver, "(//div[@role='list'])[5]", PRICE_OPTIONS)
        
#         # Отказ из-за цены
#         select_random_option(driver, "(//div[@role='list'])[6]", YES_NO)
        
#         # Хороший ассортимент (несколько вариантов)
#         select_multiple_options(driver, "(//div[@role='list'])[7]", ASSORTMENT_OPTIONS)
        
#         # Ситуации использования
#         select_multiple_options(driver, "(//div[@role='list'])[8]", USAGE_OPTIONS)
        
#         # Проблемы
#         select_multiple_options(driver, "(//div[@role='list'])[9]", PROBLEMS_OPTIONS)
        
#         # Прокрутка вниз
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         human_delay(1, 2)
        
#         # Насколько справедливой вам кажется текущая стоимость доставки?
#         select_random_option(driver, "(//div[@role='list'])[10]", ["Полностью справедлива", "Дороговато, но терпимо", "Слишком дорого"])
        
#         # Используете ли вы бонусные баллы?
#         select_random_option(driver, "(//div[@role='list'])[11]", YES_NO)
        
#         # Согласие с утверждением
#         select_random_option(driver, "(//div[@role='list'])[12]", AGREE_OPTIONS)
        
#         # Оценка интерфейса
#         rating_xpath = "(//div[@role='list'])[13]"
#         # Получаем контейнер для рейтинга
#         rating_container = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, rating_xpath)))
#         scroll_to_element(driver, rating_container)
        
#         rating_value = random.randint(1, 5)
#         rating = rating_container.find_element(By.XPATH, f".//div[@data-value='{rating_value}']")
#         safe_click(driver, rating)
        
#         # Сложно ли вам находить подходящие блюда?
#         select_random_option(driver, "(//div[@role='list'])[14]", YES_NO)
        
#         # Блок с «Частыми заказами»
#         select_random_option(driver, "(//div[@role='list'])[15]", ["Да", "Нет", "Всё равно"])
        
#         # Какие элементы приложения раздражают?
#         fill_text_field(driver, "(//div[@role='listitem'])[16]", "Нет раздражающих элементов")
        
#         # Отношение к подписке
#         select_random_option(driver, "(//div[@role='list'])[17]", ["Куплю, если цена адекватна", "Не готов платить за подписку", "Зависит от условий"])
        
#         # Важность точного времени доставки
#         select_random_option(driver, "(//div[@role='list'])[18]", ["Критически важен", "Не важен", "Хочу видеть примерный интервал"])
        
#         # Предзаказ в постамат
#         select_random_option(driver, "(//div[@role='list'])[19]", YES_NO)
        
#         # Комбо-наборы
#         select_random_option(driver, "(//div[@role='list'])[20]", AGREE_OPTIONS)
        
#         # Частота заказа одних блюд
#         select_random_option(driver, "(//div[@role='list'])[21]", FREQUENCY_OPTIONS)
        
#         # Заказ из нескольких ресторанов
#         select_random_option(driver, "(//div[@role='list'])[22]", ["Да", "Нет", "Всё равно"])
        
#         # Важность доставки лекарств
#         select_random_option(driver, "(//div[@role='list'])[23]", ["Очень важно", "Не важно"])
        
#         # Лекарства поштучно
#         select_random_option(driver, "(//div[@role='list'])[24]", AGREE_OPTIONS)
        
#         # Полезность боксов
#         select_random_option(driver, "(//div[@role='list'])[25]", BOXES_OPTIONS)
        
#         # Доставка лекарств через Яндекс
#         select_random_option(driver, "(//div[@role='list'])[26]", BOXES_OPTIONS)
        
#         # Оплата за границей
#         select_random_option(driver, "(//div[@role='list'])[27]", ["Очень важно", "Не важно"])
        
#         # Заказ SIM-карт за границей
#         select_random_option(driver, "(//div[@role='list'])[28]", ABROAD_OPTIONS)
        
#         # Точки выдачи
#         select_random_option(driver, "(//div[@role='list'])[29]", PICKUP_OPTIONS)
        
#         # Групповые заказы
#         select_random_option(driver, "(//div[@role='list'])[30]", GROUP_ORDER_OPTIONS)
        
#         # Разделение заказа
#         select_random_option(driver, "(//div[@role='list'])[31]", ["Да", "Нет"])
        
#         # Какие улучшения вы предложили бы?
#         fill_text_field(driver, "(//div[@role='listitem'])[32]", "Предложил бы улучшить интерфейс")
        
#         # Прокрутка к кнопке отправки
#         submit_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//span[text()='Отправить']/ancestor::div[@role='button']")))
#         scroll_to_element(driver, submit_button)
#         human_delay(1, 2)
        
#         # Отправка формы
#         if safe_click(driver, submit_button):
#             print("Форма отправлена!")
            
#             # Проверка успешной отправки
#             try:
#                 WebDriverWait(driver, 15).until(
#                     EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Ваш ответ записан') or contains(text(), 'Your response has been recorded')]")))
#                 print("✔ Подтверждение отправки получено")
#                 return True
#             except:
#                 print("❌ Не удалось подтвердить отправку формы")
#                 return False
#         else:
#             print("❌ Не удалось нажать кнопку отправки")
#             return False
            
#     except Exception as e:
#         print(f"❌ Критическая ошибка при заполнении формы: {str(e)}")
#         return False

# def main():
#     # Инициализация драйвера
#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=chrome_options
#     )
    
#     # Настройка параметров драйвера для маскировки
#     driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#         'source': '''
#             delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
#             delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
#             delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             window.navigator.chrome = { runtime: {}, };
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['ru-RU', 'ru']
#             });
#             Object.defineProperty(navigator, 'language', {
#                 get: () => 'ru-RU'
#             });
#         '''
#     })
    
#     # Установка русского языка
#     driver.execute_cdp_cmd('Emulation.setUserAgentOverride', {
#         "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
#         "platform": "Win32",
#         "acceptLanguage": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
#     })
    
#     success_count = 0
#     fail_count = 0
    
#     # Количество заполнений
#     total_attempts = 5  # Начните с малого числа для теста
    
#     print(f"Начало заполнения форм ({total_attempts} попыток)")
#     print("-" * 50)
    
#     for attempt in range(1, total_attempts + 1):
#         print(f"\nПопытка {attempt}/{total_attempts}:")
        
#         result = fill_form(driver)
        
#         if result:
#             success_count += 1
#             print(f"Статус: \033[92mУСПЕШНО\033[0m")
#         else:
#             fail_count += 1
#             print(f"Статус: \033[91mОШИБКА\033[0m")
        
#         # Задержка между заполнениями
#         if attempt < total_attempts:
#             delay = random.randint(120, 300)  # 2-5 минут
#             print(f"Ожидание {delay} сек. перед следующим заполнением...")
#             time.sleep(delay)
    
#     # Закрываем браузер после завершения
#     driver.quit()
    
#     # Отчет
#     print("\n" + "=" * 50)
#     print("Итоговый отчет")
#     print("=" * 50)
#     print(f"Всего попыток: {total_attempts}")
#     print(f"Успешных: \033[92m{success_count}\033[0m")
#     print(f"Неудачных: \033[91m{fail_count}\033[0m")
#     if total_attempts > 0:
#         print(f"Процент успеха: {success_count/total_attempts*100:.1f}%")
#     print("\nРабота завершена!")

# if __name__ == "__main__":
#     main()

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Настройки браузера
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfegSLrxN8kB3NHDAUg0AeCdCfxzEIqd2DONBYkyJ9G5YIacg/viewform"

# Варианты ответов (упрощенные)
AGES = ["До 18", "18-24", "25-34", "35-44", "45+"]
CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург"]
FREQUENCIES = ["Ежедневно", "Несколько раз в неделю", "Несколько раз в месяц"]
SERVICES = ["Яндекс Еда", "Самокат", "Яндекс Лавка"]
YES_NO = ["Да", "Нет"]
AGREE_OPTIONS = ["Да", "Нет", "Затрудняюсь ответить"]

def human_delay(min_sec=0.2, max_sec=1.0):
    """Сокращенные задержки"""
    time.sleep(random.uniform(min_sec, max_sec))

def safe_click(driver, element):
    """Безопасный клик с повторными попытками"""
    attempts = 0
    while attempts < 3:
        try:
            element.click()
            return True
        except (ElementClickInterceptedException, StaleElementReferenceException):
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            human_delay(0.5, 1.0)
            attempts += 1
    return False

def select_random_option(driver, container_xpath):
    """Выбирает случайный вариант ответа для вопроса"""
    try:
        container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, container_xpath))
        
        choices = container.find_elements(By.XPATH, ".//div[@role='radio']")
        if not choices:
            choices = container.find_elements(By.XPATH, ".//div[@role='checkbox']")
        
        if choices:
            random_choice = random.choice(choices)
            return safe_click(driver, random_choice)
        return False
    except:
        return False

def select_multiple_options(driver, container_xpath, max_choices=2):
    """Выбирает несколько случайных вариантов"""
    try:
        container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, container_xpath))
        
        choices = container.find_elements(By.XPATH, ".//div[@role='checkbox']")
        if choices:
            num_choices = random.randint(1, min(max_choices, len(choices)))
            selected = random.sample(choices, num_choices)
            
            for choice in selected:
                if not safe_click(driver, choice):
                    return False
                human_delay(0.1, 0.3)
            return True
        return False
    except:
        return False

def fill_text_field(driver, field_xpath, text):
    """Заполняет текстовое поле"""
    try:
        text_area = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, field_xpath)))
        
        text_area.clear()
        text_area.send_keys(text[:50])  # Ограничиваем длину текста
        return True
    except:
        return False

def fill_priorities(driver):
    """Упрощенное заполнение приоритетов"""
    try:
        # Находим все радиогруппы приоритетов
        radio_groups = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@role='radiogroup']")))
        
        for group in radio_groups[:10]:  # Первые 10 групп
            options = group.find_elements(By.XPATH, ".//div[@role='radio']")
            if options:
                random_choice = random.choice(options)
                safe_click(driver, random_choice)
                human_delay(0.1, 0.3)
        return True
    except:
        return False

def fill_form(driver):
    """Основная функция заполнения формы"""
    try:
        # Открываем форму
        driver.get(FORM_URL)
        print("Форма загружена")
        
        # Ожидаем загрузки основной части формы
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='listitem']")))
        human_delay(1, 2)
        
        # Упрощенное заполнение формы
        select_random_option(driver, "(//div[@role='list'])[1]")  # Возраст
        select_random_option(driver, "(//div[@role='list'])[2]")  # Город
        select_random_option(driver, "(//div[@role='list'])[3]")  # Частота
        select_multiple_options(driver, "(//div[@role='list'])[4]")  # Сервисы
        
        # Приоритеты
        fill_priorities(driver)
        
        # Продолжаем заполнение
        select_random_option(driver, "(//div[@role='list'])[5]")  # Цена доставки
        select_random_option(driver, "(//div[@role='list'])[6]")  # Отказ из-за цены
        
        # Оставшиеся вопросы (упрощенные)
        for i in range(7, 20):
            select_random_option(driver, f"(//div[@role='list'])[{i}]")
            human_delay(0.1, 0.3)
        
        # Текстовые поля
        fill_text_field(driver, "//textarea", "Нет комментариев")
        fill_text_field(driver, "(//textarea)[2]", "Улучшить интерфейс")
        
        # Отправка формы
        submit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Отправить']/ancestor::div[@role='button']")))
        
        if safe_click(driver, submit_button):
            print("Форма отправлена!")
            
            # Проверка успешной отправки
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Ваш ответ записан')]")))
                print("✔ Подтверждение отправки получено")
                return True
            except:
                return False
        return False
            
    except Exception as e:
        print(f"❌ Ошибка при заполнении формы: {str(e)}")
        return False

def main():
    # Инициализация драйвера
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Настройка маскировки
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.navigator.chrome = { runtime: {} };
        '''
    })
    
    success_count = 0
    fail_count = 0
    
    # Количество заполнений
    total_attempts = 300
    
    print(f"Начало заполнения форм ({total_attempts} попыток)")
    print("-" * 50)
    
    start_time = time.time()
    
    for attempt in range(1, total_attempts + 1):
        print(f"Попытка {attempt}/{total_attempts}:", end=" ", flush=True)
        
        result = fill_form(driver)
        
        if result:
            success_count += 1
            print("✓")
        else:
            fail_count += 1
            print("✗")
        
        # Минимальная задержка между заполнениями
        if attempt < total_attempts:
            delay = random.uniform(5, 15)
            time.sleep(delay)
    
    # Закрываем браузер
    driver.quit()
    
    # Расчет времени
    total_time = time.time() - start_time
    mins = int(total_time // 60)
    secs = int(total_time % 60)
    
    # Отчет
    print("\n" + "=" * 50)
    print("Итоговый отчет")
    print("=" * 50)
    print(f"Всего попыток: {total_attempts}")
    print(f"Успешных: \033[92m{success_count}\033[0m")
    print(f"Неудачных: \033[91m{fail_count}\033[0m")
    print(f"Время выполнения: {mins} мин. {secs} сек.")
    if total_attempts > 0:
        print(f"Процент успеха: {success_count/total_attempts*100:.1f}%")
        print(f"Скорость: {total_attempts/(total_time/60):.1f} форм/мин")
    print("\nРабота завершена!")

if __name__ == "__main__":
    main()