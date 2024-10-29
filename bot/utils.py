import json
import os
import threading
from datetime import datetime

import cv2
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import BASE_DIR, IMAGES_DIR
from config import CAMERAS
from config import CHROME_DRIVER_PATH, FIREFOX_DRIVER_PATH, EDGE_DRIVER_PATH

# Глобальная переменная для хранения драйвера
driver = None  # Один драйвер для всех камер
drivers = {}

# Ссылки на загрузку драйверов
driver_links = {
    "chrome": "https://developer.chrome.com/docs/chromedriver",
    "firefox": "https://geckodriver.com/download/",
    "edge": "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/"
}


def choose_driver():
    """Инициализирует драйвер один раз и использует его для всех камер."""
    global driver
    
    if driver:
        return driver

    # Проверяем и создаем папку 'drivers', если её нет
    drivers_dir = os.path.join(BASE_DIR, 'drivers')
    if not os.path.exists(drivers_dir):
        os.makedirs(drivers_dir)
        print(f"[INFO] Создана папка для драйверов: {drivers_dir}")

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
        service = None

        if choice == '1':
            driver_path = CHROME_DRIVER_PATH
            if not os.path.exists(driver_path):
                print(f"[ERROR] Драйвер Chrome не найден по пути {driver_path}.")
                print("Скачайте ChromeDriver по ссылке: https://developer.chrome.com/docs/chromedriver/")
                input("Нажмите Enter после того, как скачаете и поместите драйвер в каталог.")
            else:
                print(f"[INFO] Драйвер Chrome найден: {driver_path}")
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
                print(f"[ERROR] Драйвер Firefox не найден по пути {driver_path}.")
                print("Скачайте GeckoDriver для Firefox по ссылке: https://geckodriver.com/download/")
                input("Нажмите Enter после того, как скачаете и поместите драйвер в каталог.")
            else:
                print(f"[INFO] Драйвер Firefox найден: {driver_path}")
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
                print(f"[ERROR] Драйвер Edge не найден по пути {driver_path}.")
                print("Скачайте EdgeDriver по ссылке: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
                input("Нажмите Enter после того, как скачаете и поместите драйвер в каталог.")
            else:
                print(f"[INFO] Драйвер Edge найден: {driver_path}")
                service = EdgeService(executable_path=driver_path)
                edge_options = webdriver.EdgeOptions()
                edge_options.add_argument("--headless")
                edge_options.add_experimental_option("prefs", prefs)
                driver = webdriver.Edge(service=service, options=edge_options)
                break

        else:
            print("[ERROR] Некорректный выбор. Попробуйте снова.")

    return driver


def init_all_cameras():
    """Запускаем все камеры с использованием одного драйвера и разных вкладок."""
    global drivers
    driver = choose_driver()

    for camera_name, camera_config in CAMERAS.items():
        camera_url = camera_config.get("url")  # Получаем URL для камеры
        if not camera_url:
            print(f"[ERROR] URL для {camera_name} не найден.")
            continue

        if len(drivers) == 0:
            # Открываем первую камеру в основном окне
            print(f"[DEBUG] Инициализация драйвера для {camera_name}...")
            driver.get(camera_url)
            time.sleep(1)
        else:
            # Открываем каждую следующую камеру в новой вкладке
            print(f"[DEBUG] Открываем новую вкладку для {camera_name}...")
            driver.execute_script("window.open('');")  # Открываем новую вкладку
            driver.switch_to.window(driver.window_handles[-1])  # Переходим в новую вкладку
            driver.get(camera_url)
            time.sleep(1)

        # Сохраняем только идентификатор вкладки для каждой камеры
        drivers[camera_name] = driver.current_window_handle
        print(f"[INFO] Страница с {camera_name} открыта.")

    print("[INFO] Все камеры инициализированы.")


def refresh_driver():
    """Обновляем страницу, чтобы сессия оставалась активной."""
    global driver
    if driver:
        print("[DEBUG] Обновляем страницу видеопотока для предотвращения истечения сессии.")
        driver.refresh()
        time.sleep(5)  # Ждем, пока страница полностью обновится


def capture_image(camera_name):
    """Захватываем изображение с открытой страницы."""
    
    driver_handle = drivers.get(camera_name)
    if not driver_handle:
        print(f"[ERROR] Драйвер для {camera_name} не найден.")
        return None
    
    # Переключаемся на нужную вкладку
    driver.switch_to.window(driver_handle)
    
    # Генерируем уникальное имя файла на основе текущего времени
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_image_filename = f"capture_{timestamp}.png"
    new_image_path = os.path.join(IMAGES_DIR, new_image_filename)

    try:
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
            print(f"[INFO] Изображение сохранено и переименовано в: {new_image_path}")
            return new_image_path
        else:
            print("[ERROR] Изображение не найдено.")
            return None
    except Exception as e:
        print(f"[ERROR] Ошибка при захвате изображения: {e}")
        return None


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


def detect_cars(image, detection_line_start, detection_line_end):
    """
    Находит автомобили на картинке
    """
    # Загрузка модели и классов
    path_conf = "./resources/yolov4-tiny.cfg"
    path_weights = "./resources/yolov4-tiny.weights"

    print("[DEBUG] Загружаем модель YOLO...")
    net = cv2.dnn.readNetFromDarknet(path_conf, path_weights)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    height, width, _ = image.shape

    # Детекция автомобилей
    blob = cv2.dnn.blobFromImage(image, 0.00392, (608, 608), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Обработка результатов детекции
    boxes = []
    confidences = []
    class_ids = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Детектируем только автомобили (class_id == 2 для COCO dataset)
            if confidence > 0.3 and class_id == 2:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # Проверка положения относительно линии детекции
                if y >= detection_line_start[1] + (detection_line_end[1] - detection_line_start[1]) * (x / width):
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

    # Применение NMS для устранения перекрывающихся боксов
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.4)
    detected_cars = [boxes[i[0]] if isinstance(i, np.ndarray) else boxes[i] for i in indices]
    return detected_cars


def get_parking_occupancy(camera_name, detected_cars, parking_spaces_path):
    """
    Проверяет занятость парковочных мест
    """
    try:
        with open(parking_spaces_path, 'r') as f:
            parking_spaces_abs = json.load(f)
        print(f"[DEBUG] Загрузка координат парковочных мест из {parking_spaces_path}")
    except FileNotFoundError:
        print(f"[ERROR] Файл с координатами парковочных мест не найден: {parking_spaces_path}")
        return None

    parking_occupancy = []
    for idx, space_abs in enumerate(parking_spaces_abs):
        x, y, w, h = space_abs

        is_occupied = False
        for car in detected_cars:
        # Вычисление IoU между парковочным местом и автомобилем
            iou = compute_iou([x, y, w, h], car)
            if iou > 0.45:  # Порог перекрытия
                is_occupied = True
                break
        parking_occupancy.append(is_occupied)

    #Реверсим лист для bv_station, так как на схеме парковка представлена с другой перспективы
    if camera_name == "bv_station":
        parking_occupancy.reverse()
    return parking_occupancy


def process_image(camera_name, detection_line_start, detection_line_end):
    """
    Обрабатывает изображение с использованием YOLO и определяет занятость парковочных мест.
    
    Args:
        camera_name: название камеры
        detection_line_start: начальная точка линии детекции (x, y)
        detection_line_end: конечная точка линии детекции (x, y)
    """
    #Захват изображения с камеры
    captured_image_path = capture_image(camera_name)
    if captured_image_path is None:
        return None

    # Загрузка и предобработка изображения
    print(f"[DEBUG] Загружаем изображение: {captured_image_path}")
    image = cv2.imread(captured_image_path)
    image = adjust_brightness(image, factor=1.5)
    image = increase_contrast(image)
    image = upscale_image(image, scale_factor=1.5)
    height, width, _ = image.shape

    # Загрузка и предобработка изображения
    print(f"[DEBUG] Загружаем изображение: {captured_image_path}")
    image = cv2.imread(captured_image_path)
    image = adjust_brightness(image, factor=1.5)
    image = increase_contrast(image)
    image = upscale_image(image, scale_factor=1.5)

    height, width, _ = image.shape

    # Преобразование координат линии детекции
    detection_line_start = (int(detection_line_start[0] * width), int(detection_line_start[1] * height))
    detection_line_end = (int(detection_line_end[0] * width), int(detection_line_end[1] * height))

    detected_cars = detect_cars(image, detection_line_start, detection_line_end)
    # Отрисовка детектированных автомобилей
    for car in detected_cars:
        x, y, w, h = car
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)
        cv2.putText(image, "CAR", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    parking_spaces_path = "./resources/parking_spaces/" + camera_name + ".json"
    try:
        with open(parking_spaces_path, 'r') as f:
            parking_spaces_abs = json.load(f)
        print(f"[DEBUG] Загрузка координат парковочных мест из {parking_spaces_path}")

        # Проверка занятости парковочных мест
        for idx, space_abs in enumerate(parking_spaces_abs):
            x, y, w, h = space_abs

            is_occupied = False
            for car in detected_cars:
                # Вычисление IoU между парковочным местом и автомобилем
                iou = compute_iou([x, y, w, h], car)
                if iou > 0.45:  # Порог перекрытия
                    is_occupied = True
                    break

            # Отрисовка парковочного места
            color = (0, 0, 255) if is_occupied else (0, 255, 0)
            label = "OCCUPIED" if is_occupied else "FREE"
            cv2.rectangle(image,
                          (x, y),
                          (x + w, y + h),
                          color, 2)
            cv2.putText(image, label,
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    except FileNotFoundError:
        print(f"[ERROR] Файл с координатами парковочных мест не найден: {parking_spaces_path}")

    # Сохранение результата
    result_image_path = os.path.join(IMAGES_DIR, "processed_" + os.path.basename(captured_image_path))
    cv2.imwrite(result_image_path, image)
    
    print(f"[INFO] Изображение сохранено по пути: {result_image_path}")
    return result_image_path


def draw_parking_on_scheme(camera_name, detection_line_start, detection_line_end):
    """
    Рисует занятость парковочных мест на схеме парковки.

    Args:
        camera_name: название камеры
        detection_line_start: начальная точка линии детекции (x, y)
        detection_line_end: конечная точка линии детекции (x, y)
    """

    #Захват изображения с камеры
    captured_image_path = capture_image(camera_name)
    if captured_image_path is None:
        return None

    #Загрузка схемы парковки
    parking_scheme_path = "./resources/parking_schemes/" + camera_name + ".png"
    scheme_image = cv2.imread(parking_scheme_path)
    if scheme_image is None:
        print(f"[ERROR] Невозможно загрузить схему: {parking_scheme_path}")
        return None
    print(f"[INFO] Загружена схема парковки: {parking_scheme_path}")

    # Загрузка и предобработка изображения
    print(f"[DEBUG] Загружаем изображение: {captured_image_path}")
    image = cv2.imread(captured_image_path)
    image = adjust_brightness(image, factor=1.5)
    image = increase_contrast(image)
    image = upscale_image(image, scale_factor=1.5)
    height, width, _ = image.shape

    detected_cars = detect_cars(image, detection_line_start, detection_line_end)

    #Вычисление занятости парковки
    parking_spaces_path = "./resources/parking_spaces/" + camera_name + ".json"
    parking_occupancy = get_parking_occupancy(camera_name, detected_cars, parking_spaces_path)
    if parking_occupancy is None:
        return None

    #Загрузка файла с координатами парковочных мест на схеме
    parking_scheme_spaces_path = "./resources/parking_schemes_spaces/" + camera_name + ".json"
    try:
        with open(parking_scheme_spaces_path, 'r') as f:
            parking_scheme_spaces = json.load(f)
        print(f"[DEBUG] Загрузка координат парковочных мест на схеме из {parking_scheme_spaces_path}")
    except FileNotFoundError:
        print(f"[ERROR] Файл с координатами парковочных мест на схеме не найден: {parking_scheme_spaces_path}")
        return None

    # Отрисовка парковочных мест
    for idx, space in enumerate(parking_scheme_spaces):
        x1, y1, x2, y2 = space
        color = (0, 0, 255) if parking_occupancy[idx] else (0, 255, 0)  # Красный для занятых, зелёный для свободных
        # Рисуем прямоугольник на парковочном месте
        cv2.rectangle(scheme_image, (x1, y1), (x2, y2), color, -1)

    # Сохранение результата со схемой и отметками парковочных мест
    result_image_path = os.path.join(IMAGES_DIR, "prosecced_" + os.path.basename(parking_scheme_path))
    cv2.imwrite(result_image_path, scheme_image)
    print(f"[INFO] Схема парковки с отметкой мест сохранена по пути: {result_image_path}")
    return result_image_path


def compute_iou(box1, box2):
    """
    Вычисляет IoU (Intersection over Union) между двумя боксами.
    
    Args:
        box1: [x1, y1, w1, h1]
        box2: [x2, y2, w2, h2]
    """
    # Преобразование в формат [x1, y1, x2, y2]
    b1 = [box1[0], box1[1], box1[0] + box1[2], box1[1] + box1[3]]
    b2 = [box2[0], box2[1], box2[0] + box2[2], box2[1] + box2[3]]
    
    # Определение координат пересечения
    x_left = max(b1[0], b2[0])
    y_top = max(b1[1], b2[1])
    x_right = min(b1[2], b2[2])
    y_bottom = min(b1[3], b2[3])
    
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = (b1[2] - b1[0]) * (b1[3] - b1[1])
    box2_area = (b2[2] - b2[0]) * (b2[3] - b2[1])
    
    iou = intersection_area / float(box1_area + box2_area - intersection_area)
    return max(0.0, min(iou, 1.0))


def clear_images_dir():
    """Удаляет все файлы в папке IMAGES_DIR."""

    images_dir = os.path.join(BASE_DIR, 'data', 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"[INFO] Создана папка для драйверов: {images_dir}")

    try:
        for file in os.listdir(IMAGES_DIR):
            file_path = os.path.join(IMAGES_DIR, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        print(f"[INFO] Все файлы в папке {IMAGES_DIR} удалены.")
    except Exception as e:
        print(f"[ERROR] Ошибка при очистке папки: {e}")


def close_drivers():
    """Закрываем все драйверы для всех камер."""
    global drivers
    for camera_name, driver in drivers.items():
        if driver:
            print(f"[DEBUG] Закрываем драйвер для {camera_name}...")
            driver.quit()
    drivers.clear()
    print("[INFO] Все драйверы закрыты.")


def periodic_refresh(interval=10):
    """Периодически обновляет страницы видеопотоков каждые interval минут."""
    global driver
    while True:
        time.sleep(interval * 60)
        print("[DEBUG] Обновление всех видеопотоков...")
        for camera_name, driver_handle in drivers.items():
            if driver_handle:
                try:
                    # Переключаемся на вкладку камеры
                    driver.switch_to.window(driver_handle)
                    print(f"[DEBUG] Обновляем видеопоток для {camera_name}...")
                    driver.refresh()
                    time.sleep(1)  # Ждем, пока страница обновится
                except Exception as e:
                    print(f"[ERROR] Ошибка при обновлении {camera_name}: {e}")


# Вызовем функцию обновления в отдельном потоке, чтобы она работала фоном каждые 10 минут
threading.Thread(target=periodic_refresh, args=(10,), daemon=True).start()