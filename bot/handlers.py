from aiogram import types, Dispatcher
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils import clear_images_dir, process_image, draw_parking_on_scheme
from config import CAMERAS


# Define the CallbackData subclass
class CameraCallback(CallbackData, prefix="camera"):
    name: str


async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Я бот поиска свободных мест на парковке. Отправь команду /capture, чтобы выбрать парковку."
    )


async def send_camera_options(message: types.Message):
    builder = InlineKeyboardBuilder()
    for camera_id, camera_info in CAMERAS.items():
        builder.button(
            text=camera_info['title'],  # Используем название камеры из 'title'
            callback_data=CameraCallback(name=camera_id)  # Передаем идентификатор камеры
        )
    builder.adjust(1)  # Adjusts the keyboard to have 1 button per row
    await message.answer("Выберите парковку:", reply_markup=builder.as_markup())


async def handle_camera_choice(callback_query: types.CallbackQuery, callback_data: CameraCallback):
    camera_name = callback_data.name

    await callback_query.message.answer(
        f"Пожалуйста, подождите, идет захват изображения с {CAMERAS[camera_name]['title']}..."
    )

    clear_images_dir()

    # Получаем конфигурацию камеры (url и границы детекции)
    camera_config = CAMERAS.get(camera_name, {})
    camera_url = camera_config.get("url")
    detection_line_start = camera_config.get("detection_line_start")
    detection_line_end = camera_config.get("detection_line_end")
    
    if (camera_url is None or
        detection_line_start is None or
        detection_line_end is None):
        await callback_query.message.answer(f"Неизвестная парковка: {CAMERAS[camera_name]['title']}.")
        return

    scheme_image_path = draw_parking_on_scheme(camera_name, detection_line_start, detection_line_end)
    processed_image_path, photo_image_path = process_image(camera_name, detection_line_start, detection_line_end)
    if scheme_image_path is not None:
        scheme_image = FSInputFile(scheme_image_path)
        photo_image = FSInputFile(photo_image_path)
        
        await callback_query.message.answer_photo(
            scheme_image,
            caption=f"Схема парковки на {CAMERAS[camera_name]['title']} с указанием свободных и занятых мест! Зеленые - свободные, красные - занятые."
        )
        await callback_query.message.answer_photo(
            photo_image,
            caption="Вот фотография парковки!"
        )
        return


    if processed_image_path is not None:
        image = FSInputFile(processed_image_path)
        await callback_query.message.answer_photo(
            image,
            caption=f"Вот изображение с {CAMERAS[camera_name]['title']} с распознанными объектами!",
        )
        return

    await callback_query.message.answer(f"Не удалось захватить изображение с {CAMERAS[camera_name]['title']}.")


def register_handlers(dp: Dispatcher):
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(send_camera_options, Command("capture"))
    dp.callback_query.register(handle_camera_choice, CameraCallback.filter())
