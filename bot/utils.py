import os
import cv2
import numpy as np
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from config import BASE_DIR ,IMAGES_DIR
import threading
import platform
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from config import CHROME_DRIVER_PATH, FIREFOX_DRIVER_PATH, EDGE_DRIVER_PATH

# Глобальная переменная для хранения драйвера
driver = None

# Ссылки на загрузку драйверов
driver_links = {
    "chrome": "https://developer.chrome.com/docs/chromedriver",
    "firefox": "https://geckodriver.com/download/",
    "edge": "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/"
}

def choose_driver():
    """Определяет, какой браузер использовать и проверяет наличие драйвера."""
    
    # Проверяем и создаем папку 'drivers', если её нет
    drivers_dir = os.path.join(BASE_DIR, 'drivers')
    if not os.path.exists(drivers_dir):
        os.makedirs(drivers_dir)
        print(f"Создана папка для драйверов: {drivers_dir}")

    prefs = {
        "download.default_directory": IMAGES_DIR,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }

    while True:
        print("Выберите браузер для использования:")
        print("1. Chrome")
        print("2. Firefox")
        print("3. Edge")
        
        choice = input("Введите номер браузера (1/2/3): ").strip()

        driver_path = None
        driver = None
        service = None

        if choice == '1':
            driver_path = CHROME_DRIVER_PATH
            if not os.path.exists(driver_path):
                print(f"Драйвер Chrome не найден по пути {driver_path}.")
                print("Скачайте ChromeDriver по ссылке: https://developer.chrome.com/docs/chromedriver/")
                input("Нажмите Enter после того, как скачаете и поместите драйвер в каталог.")
            else:
                print(f"Драйвер Chrome найден: {driver_path}")
                service = ChromeService(executable_path=driver_path)
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_experimental_option("prefs", prefs)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                break

        elif choice == '2':
            driver_path = FIREFOX_DRIVER_PATH
            if not os.path.exists(driver_path):
                print(f"Драйвер Firefox не найден по пути {driver_path}.")
                print("Скачайте GeckoDriver для Firefox по ссылке: https://geckodriver.com/download/")
                input("Нажмите Enter после того, как скачаете и поместите драйвер в каталог.")
            else:
                print(f"Драйвер Firefox найден: {driver_path}")
                service = FirefoxService(executable_path=driver_path)
                firefox_options = webdriver.FirefoxOptions()
                firefox_options.add_argument("--headless")

                # Настройка для сохранения файлов в Firefox
                firefox_options.set_preference("browser.download.folderList", 2)
                firefox_options.set_preference("browser.download.dir", IMAGES_DIR)
                firefox_options.set_preference("browser.download.useDownloadDir", True)
                firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/png")

                driver = webdriver.Firefox(service=service, options=firefox_options)
                break

        elif choice == '3':
            driver_path = EDGE_DRIVER_PATH
            if not os.path.exists(driver_path):
                print(f"Драйвер Edge не найден по пути {driver_path}.")
                print("Скачайте EdgeDriver по ссылке: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
                input("Нажмите Enter после того, как скачаете и поместите драйвер в каталог.")
            else:
                print(f"Драйвер Edge найден: {driver_path}")
                service = EdgeService(executable_path=driver_path)
                edge_options = webdriver.EdgeOptions()
                edge_options.add_argument("--headless")
                edge_options.add_experimental_option("prefs", prefs)
                driver = webdriver.Edge(service=service, options=edge_options)
                break

        else:
            print("Некорректный выбор. Попробуйте снова.")

    return driver

def init_driver():
    """Инициализируем драйвер и открываем страницу с видеопотоком один раз."""
    global driver
    if driver is None:
        # Выбираем браузер
        driver = choose_driver()

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

def adjust_brightness(image, factor=1.2):
    """
    Увеличивает яркость изображения.
    :param image: исходное изображение (в формате BGR).
    :param factor: коэффициент яркости, где 1.0 - это оригинальная яркость.
    :return: изображение с увеличенной яркостью.
    """
    # Преобразуем изображение в цветовое пространство HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Увеличиваем яркость
    h, s, v = cv2.split(hsv)
    v = cv2.multiply(v, factor)
    
    # Ограничиваем значение яркости, чтобы оно не превышало 255
    v = np.clip(v, 0, 255).astype(np.uint8)
    
    # Объединяем каналы обратно
    hsv = cv2.merge([h, s, v])
    
    # Преобразуем обратно в BGR
    bright_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return bright_image

def upscale_image(image, scale_factor=2):
    """Увеличивает разрешение изображения."""
    width = int(image.shape[1] * scale_factor)
    height = int(image.shape[0] * scale_factor)
    dim = (width, height)
    upscaled_image = cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR)
    return upscaled_image

def increase_contrast(image):
    """Увеличивает контраст изображения с помощью CLAHE."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)  # Преобразуем в цветовое пространство LAB
    l, a, b = cv2.split(lab)  # Разделяем каналы
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))  # Создаем объект CLAHE
    cl = clahe.apply(l)  # Применяем CLAHE к L-каналу (яркость)
    limg = cv2.merge((cl, a, b))  # Объединяем каналы обратно
    enhanced_image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)  # Преобразуем обратно в BGR
    return enhanced_image

def process_image(image_path):
    """Обрабатывает изображение с использованием YOLO и распознает машины только в заданной области."""
    # Путь до конфигурации и весов модели YOLO (указываем из папки Resources)
    path_conf = "./resources/yolov4-tiny.cfg"
    path_weights = "./resources/yolov4-tiny.weights"
    path_coco_names = "./resources/coco.names.txt"

    # Загрузка классов объектов (например, машины, велосипеды и т.д.)
    with open(path_coco_names, 'r') as f:
        classes = [line.strip() for line in f.readlines()]

    print("[DEBUG] Загружаем классы объектов...")
    print(f"[DEBUG] Классы загружены: {classes}")

    # Загрузка модели YOLO
    print("[DEBUG] Загружаем модель YOLO...")
    net = cv2.dnn.readNetFromDarknet(path_conf, path_weights)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    print(f"[DEBUG] Выходные слои: {output_layers}")

    # Загрузка изображения
    print(f"[DEBUG] Загружаем изображение: {image_path}")
    image = cv2.imread(image_path)

    # Увеличиваем яркость
    image = adjust_brightness(image, factor=1.5)
    
    # Повышаем контраст
    image = increase_contrast(image)
    
    # Увеличиваем разрешение
    image = upscale_image(image, scale_factor=1.5)  # Повышаем разрешение на 50%

    height, width, _ = image.shape
    print(f"[DEBUG] Размеры изображения: ширина={width}, высота={height}")

    # Подготовка изображения для YOLO с размером 608x608
    print("[DEBUG] Подготавливаем изображение для YOLO...")
    blob = cv2.dnn.blobFromImage(image, 0.00392, (608, 608), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Определяем угловую область для детекции (например, более низкая слева и более высокая справа)
    detection_line_start = (0, int(height * 0.68))  # Левый конец линии ниже (70% высоты)
    detection_line_end = (width, int(height * 0.35))  # Правый конец линии выше (40% высоты)

    # Отрисовка наклонной границы на изображении
    cv2.line(image, detection_line_start, detection_line_end, (0, 0, 255), 2)  # Красная линия

    # Постобработка - извлекаем координаты найденных объектов
    class_ids = []
    confidences = []
    boxes = []

    print(f"[DEBUG] Количество обнаруженных объектов (raw output): {len(outs)}")
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.2:  # Точность более 30%
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Координаты верхнего левого угла
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # Проверяем, находится ли объект ниже наклонной линии (условие с использованием уравнения линии)
                if y >= detection_line_start[1] + (detection_line_end[1] - detection_line_start[1]) * (x / width):
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

    print(f"[DEBUG] Найдено объектов: {len(boxes)}")

    # Убираем пересекающиеся области
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.4)
    print(f"[DEBUG] Осталось объектов после NMS: {len(indices)}")

    # Отрисовка результатов на изображении
    if len(indices) > 0:  # Проверка, есть ли объекты для обработки
        for i in indices:
            if isinstance(i, np.ndarray):  # Проверяем, является ли i массивом
                i = i[0]  # Если это массив, берем первый элемент
            box = boxes[i]
            x, y, w, h = box
            label = str(classes[class_ids[i]])
            color = (0, 255, 0)
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    else:
        print("Не удалось найти объекты на изображении.")

    # Сохраняем изображение с результатами
    result_image_path = os.path.join(IMAGES_DIR, "processed_" + os.path.basename(image_path))
    cv2.imwrite(result_image_path, image)
    
    print(f"[DEBUG] Изображение сохранено по пути: {result_image_path}")
    return result_image_path


def clear_images_dir():
    """Удаляет все файлы в папке IMAGES_DIR."""

    images_dir = os.path.join(BASE_DIR, 'data', 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"Создана папка для драйверов: {images_dir}")

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
