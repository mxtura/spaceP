import os

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
API_TOKEN = '7386973554:AAH3VAP9AW0URsm9n_vCyrfjIzt9LOo-9Vw'

# Ссылки на камеры
CAMERAS = {
    "cam 1": {
        "title": "Вокзал БВ",
        "url": "https://cctv.tmpk.net/dubna.vokzal.bolshaya.volga..na.sajt-eef379341e/embed.html?autoplay=true&play_duration=600&token=3.wd_jz8txAAAAAAAAAAEABh7pwDgdfWpsYhspsa0WeIoUtabnbFLJMp6Q",
        "detection_line_start": (0, 0.68),
        "detection_line_end": (1.0, 0.35)
    }
}

# Базовый путь проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Путь к папке с изображениями
IMAGES_DIR = os.path.join(BASE_DIR, 'data', 'images')

# Определение расширения драйверов в зависимости от операционной системы
DRIVER_EXTENSION = '.exe' if os.name == 'nt' else ''

# Пути к драйверам для разных браузеров без учета расширения
CHROME_DRIVER_PATH = os.path.join(BASE_DIR, 'drivers', f'chromedriver{DRIVER_EXTENSION}')
FIREFOX_DRIVER_PATH = os.path.join(BASE_DIR, 'drivers', f'geckodriver{DRIVER_EXTENSION}')
EDGE_DRIVER_PATH = os.path.join(BASE_DIR, 'drivers', f'msedgedriver{DRIVER_EXTENSION}')
