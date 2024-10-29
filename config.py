import os

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
API_TOKEN = '7386973554:AAH3VAP9AW0URsm9n_vCyrfjIzt9LOo-9Vw'

# Ссылки на камеры
#WARNING: названия камер должны совпадать с соответствующими файлами из:
#resources/parking_spaces
#resources/parking_schemes_spaces
#resources/parking_schemes
CAMERAS = {
    "bv_station": {
        "title": "Вокзал БВ",
        "url": "https://cctv.tmpk.net/dubna.vokzal.bolshaya.volga..na.sajt-eef379341e/embed.html?autoplay=true&play_duration=600&token=3.wd_jz8txAAAAAAAAAAEABh7pwDgdfWpsYhspsa0WeIoUtabnbFLJMp6Q",
        "detection_line_start": (0, 0.68),
        "detection_line_end": (1.0, 0.35)
    },
    "enth_strt": {
        "title": "улица Энтузиастов",
        "url": "https://cctv.tmpk.net/entuziastov.1512.parkovka.na.entuziastov-ccb5aca411/embed.html?autoplay=true&play_duration=600&token=3.ihzhG497AAAAAAAAAAEABeMyAzO0Xs7qTEMli4PIvCR3v9lg-hgPvd8B",
        "detection_line_start": (0, 0),
        "detection_line_end": (1.0, 0)
    },
    "tvrsk_vol_intrsec": {
        "title": "перекресток Тверской и Володарского",
        "url": "https://cctv.tmpk.net/dubna.perekrestok.tverskoj.i.volodarskogo..na.sajt-40e93ccb7f/embed.html?autoplay=true&play_duration=600&token=3.wd_jz8txAAAAAAAAAAEABh7pwDgdfapwxOwLlSExJ6w6F0GPTilhxd_M",
        "detection_line_start": (0, 0),
        "detection_line_end": (1.0, 0)
    },
    "blshvlzh_intersec": {
        "title": "перекресток ул. Большеволжская",
        "url": "https://cctv.tmpk.net/dubna.bolshevolzhskaya...na.sajt-c6b04b442d/embed.html?autoplay=true&play_duration=600&token=3.wd_jz8txAAAAAAAAAAEABh7pwDgdfV55JJGGAxTbNHJdXHwp0G-TWcR5",
        "detection_line_start": (0, 0),
        "detection_line_end": (1.0, 0)
    },
    "bglb_33_pkng_ave": {
        "title": "Боголюбова 33, парковка у проспекта",
        "url": "https://cctv.tmpk.net/bogolyubova.33.parkovka.u.prospekta.-a22767b02f/embed.html?autoplay=true&play_duration=600&token=3.EV2sp585AAAAAAAAAAEABfmGw-PyQmQpJ5rxEHJ7DcIsk1aHEUe-7Wrt",
        "detection_line_start": (0, 0),
        "detection_line_end": (1.0, 0)
    },
    "enth_15_12_9may_pk": {
        "title": "Энтузиастов 15/12, Парковка на 9 мая",
        "url": "https://cctv.tmpk.net/entuziastov.1512.parkovka.na.9.maya-81028c7665/embed.html?autoplay=true&play_duration=600&token=3.EV2sp585AAAAAAAAAAEABfmGw-PyQhhqN3kVKeJObcLBOZAry7efAZs9",
        "detection_line_start": (0, 0),
        "detection_line_end": (1.0, 0)
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
