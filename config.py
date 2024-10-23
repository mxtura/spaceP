import os

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
API_TOKEN = '7386973554:AAH3VAP9AW0URsm9n_vCyrfjIzt9LOo-9Vw'

# Базовый путь проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Путь к папке с изображениями
IMAGES_DIR = os.path.join(BASE_DIR, 'data', 'images')

# Пути к драйверам для разных браузеров
CHROME_DRIVER_PATH = os.path.join(BASE_DIR, 'drivers', 'chromedriver.exe')  # Путь к ChromeDriver
FIREFOX_DRIVER_PATH = os.path.join(BASE_DIR, 'drivers', 'geckodriver.exe')  # Путь к GeckoDriver (Firefox)
EDGE_DRIVER_PATH = os.path.join(BASE_DIR, 'drivers', 'msedgedriver.exe')    # Путь к EdgeDriver
