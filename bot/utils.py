import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from config import IMAGES_DIR
import threading

# Глобальная переменная для хранения драйвера
driver = None

def init_driver():
    """Инициализируем драйвер и открываем страницу с видеопотоком один раз."""
    global driver
    if driver is None:
        # Настройка ChromeDriver для Selenium
        service = Service('/usr/bin/chromedriver')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Настройка для сохранения файлов
        prefs = {
            "download.default_directory": IMAGES_DIR,
            "download.prompt_for_download": False,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # Инициализация драйвера
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Драйвер инициализирован. Открываем страницу с видеопотоком...")

        # Открываем страницу с видеопотоком
        driver.get("https://cctv.tmpk.net/dubna.vokzal.bolshaya.volga..na.sajt-eef379341e/embed.html?autoplay=true&play_duration=600&token=3.wd_jz8txAAAAAAAAAAEABh7pwDgdfWpsYhspsa0WeIoUtabnbFLJMp6Q")
        time.sleep(5)  # Ждем загрузки страницы
        print("Страница с видеопотоком открыта.")

def refresh_driver():
    """Обновляем страницу, чтобы сессия оставалась активной."""
    global driver
    if driver:
        print("Обновляем страницу видеопотока для предотвращения истечения сессии.")
        driver.refresh()
        time.sleep(5)  # Ждем, пока страница полностью обновится

def capture_image():
    """Захватываем изображение с открытой страницы."""
    # Генерируем уникальное имя файла на основе текущего времени
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_image_filename = f"capture_{timestamp}.png"
    new_image_path = os.path.join(IMAGES_DIR, new_image_filename)

    try:
        init_driver()  # Инициализация драйвера, если он еще не запущен

        # Эмулируем наведение на панель
        panel = driver.find_element(By.CLASS_NAME, 'media-control')
        actions = ActionChains(driver)
        actions.move_to_element(panel).perform()

        # Ждем, пока кнопка станет кликабельной
        capture_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'Flussonic.capture.plugin.media-control-button.media-control-icon'))
        )
        capture_button.click()

        time.sleep(2)  # Ждем завершения процесса сохранения

        # Проверяем наличие новых файлов в папке
        files = os.listdir(IMAGES_DIR)
        screenshot_file = None

        # Поиск файла с именем, сгенерированным автоматически плеером
        for file in files:
            if file.startswith("screenshot") and file.endswith(".jpg"):
                screenshot_file = file
                break

        # Если файл найден, переименовываем его
        if screenshot_file:
            original_image_path = os.path.join(IMAGES_DIR, screenshot_file)
            os.rename(original_image_path, new_image_path)
            print(f"Изображение сохранено и переименовано в: {new_image_path}")
            return True, new_image_path
        else:
            print("Изображение не найдено.")
            return False, None
    except Exception as e:
        print(f"Ошибка при захвате изображения: {e}")
        return False, None

def clear_images_dir():
    """Удаляет все файлы в папке IMAGES_DIR."""
    try:
        for file in os.listdir(IMAGES_DIR):
            file_path = os.path.join(IMAGES_DIR, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        print(f"Все файлы в папке {IMAGES_DIR} удалены.")
    except Exception as e:
        print(f"Ошибка при очистке папки: {e}")

def close_driver():
    """Закрываем драйвер при завершении работы бота."""
    global driver
    if driver:
        driver.quit()
        driver = None
        print("Драйвер закрыт.")

def periodic_refresh(interval):
    """Периодически обновляет страницу каждые `interval` минут."""
    while True:
        time.sleep(interval * 60)
        refresh_driver()

# Вызовем функцию обновления в отдельном потоке, чтобы она работала фоном каждые 10 минут
threading.Thread(target=periodic_refresh, args=(10,), daemon=True).start()
