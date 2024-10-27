import os
import cv2
import numpy as np
import time
import json
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
from config import CAMERAS

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

def init_all_cameras():
    """Запускаем все камеры с использованием одного драйвера и разных вкладок."""
    global drivers
    driver = choose_driver()

    for camera_name, camera_config in CAMERAS.items():
        camera_url = camera_config.get("url")  # Получаем URL для камеры
        if not camera_url:
            print(f"URL для {camera_name} не найден.")
            continue

        if len(drivers) == 0:
            # Открываем первую камеру в основном окне
            print(f"Инициализация драйвера для {camera_name}...")
            driver.get(camera_url)
            time.sleep(1)
        else:
            # Открываем каждую следующую камеру в новой вкладке
            print(f"Открываем новую вкладку для {camera_name}...")
            driver.execute_script("window.open('');")  # Открываем новую вкладку
            driver.switch_to.window(driver.window_handles[-1])  # Переходим в новую вкладку
            driver.get(camera_url)
            time.sleep(1)

        # Сохраняем только идентификатор вкладки для каждой камеры
        drivers[camera_name] = driver.current_window_handle
        print(f"Страница с {camera_name} открыта.")

    print("Все камеры инициализированы.")
	

def refresh_driver():
    """Обновляем страницу, чтобы сессия оставалась активной."""
    global driver
    if driver:
        print("Обновляем страницу видеопотока для предотвращения истечения сессии.")
        driver.refresh()
        time.sleep(5)  # Ждем, пока страница полностью обновится

def capture_image(camera_name):
    """Захватываем изображение с открытой страницы."""
    
    driver_handle = drivers.get(camera_name)
    if not driver_handle:
        print(f"Драйвер для {camera_name} не найден.")
        return False, None
    
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

def process_image(image_path, camera_name, detection_line_start, detection_line_end):
    """
    Обрабатывает изображение с использованием YOLO и определяет занятость парковочных мест.
    
    Args:
        image_path: путь к изображению
        camera_name: название камеры
        detection_line_start: начальная точка линии детекции (x, y)
        detection_line_end: конечная точка линии детекции (x, y)
    """
    
    # Загрузка модели и классов
    path_conf = "./resources/yolov4-tiny.cfg"
    path_weights = "./resources/yolov4-tiny.weights"
    path_coco_names = "./resources/coco.names.txt"

    with open(path_coco_names, 'r') as f:
        classes = [line.strip() for line in f.readlines()]

    print("[DEBUG] Загружаем модель YOLO...")
    net = cv2.dnn.readNetFromDarknet(path_conf, path_weights)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    # Загрузка и предобработка изображения
    print(f"[DEBUG] Загружаем изображение: {image_path}")
    image = cv2.imread(image_path)
    image = adjust_brightness(image, factor=1.5)
    image = increase_contrast(image)
    image = upscale_image(image, scale_factor=1.5)

    height, width, _ = image.shape
    
    # Загрузка координат парковочных мест из JSON
    json_path = f"./resources/parking_spaces.json"
    try:
        with open(json_path, 'r') as f:
            parking_spaces_abs = json.load(f)
        print(f"[DEBUG] Загружены координаты парковочных мест из {json_path}")
    except FileNotFoundError:
        print(f"[ERROR] Файл с координатами парковочных мест не найден: {json_path}")
        return None
    
    # Преобразование координат линии детекции
    detection_line_start = (int(detection_line_start[0] * width), int(detection_line_start[1] * height))
    detection_line_end = (int(detection_line_end[0] * width), int(detection_line_end[1] * height))
    
    # Отрисовка линии детекции
    cv2.line(image, detection_line_start, detection_line_end, (0, 0, 255), 2)

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

    # Отрисовка детектированных автомобилей
    for car in detected_cars:
        x, y, w, h = car
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)
        cv2.putText(image, "CAR", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    # Сохранение результата
    result_image_path = os.path.join(IMAGES_DIR, "processed_" + os.path.basename(image_path))
    cv2.imwrite(result_image_path, image)
    
    print(f"[DEBUG] Изображение сохранено по пути: {result_image_path}")
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
        print(f"Создана папка для драйверов: {images_dir}")

    try:
        for file in os.listdir(IMAGES_DIR):
            file_path = os.path.join(IMAGES_DIR, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        print(f"Все файлы в папке {IMAGES_DIR} удалены.")
    except Exception as e:
        print(f"Ошибка при очистке папки: {e}")

def close_drivers():
    """Закрываем все драйверы для всех камер."""
    global drivers
    for camera_name, driver in drivers.items():
        if driver:
            print(f"Закрываем драйвер для {camera_name}...")
            driver.quit()
    drivers.clear()
    print("Все драйверы закрыты.")

def periodic_refresh(interval=10):
    """Периодически обновляет страницы видеопотоков каждые interval минут."""
    global driver
    while True:
        time.sleep(interval * 60)
        print("Обновление всех видеопотоков...")
        for camera_name, driver_handle in drivers.items():
            if driver_handle:
                try:
                    # Переключаемся на вкладку камеры
                    driver.switch_to.window(driver_handle)
                    print(f"Обновляем видеопоток для {camera_name}...")
                    driver.refresh()
                    time.sleep(1)  # Ждем, пока страница обновится
                except Exception as e:
                    print(f"Ошибка при обновлении {camera_name}: {e}")


# Вызовем функцию обновления в отдельном потоке, чтобы она работала фоном каждые 10 минут
threading.Thread(target=periodic_refresh, args=(10,), daemon=True).start()
