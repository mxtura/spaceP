from aiogram import types, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardButton, FSInputFile
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.utils import capture_image, clear_images_dir, process_image
from config import CAMERAS

# Define the CallbackData subclass
class CameraCallback(CallbackData, prefix="camera"):
    name: str

async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Я бот, который отправляет кадр с выбранной камеры. Отправь команду /capture, чтобы выбрать камеру."
    )

async def send_camera_options(message: types.Message):
    builder = InlineKeyboardBuilder()
    for camera_id, camera_info in CAMERAS.items():
        builder.button(
            text=camera_info['title'],  # Используем название камеры из 'title'
            callback_data=CameraCallback(name=camera_id)  # Передаем идентификатор камеры
        )
    builder.adjust(1)  # Adjusts the keyboard to have 1 button per row
    await message.answer("Выберите камеру:", reply_markup=builder.as_markup())

async def handle_camera_choice(callback_query: types.CallbackQuery, callback_data: CameraCallback):
    camera_name = callback_data.name

    await callback_query.message.answer(
        f"Пожалуйста, подождите, идет захват изображения с {CAMERAS[camera_name]['title']}..."
    )

    clear_images_dir()

    # Получаем конфигурацию камеры (url и границы детекции)
    camera_config = CAMERAS.get(camera_name, {})
    camera_url = camera_config.get("url")  # Извлекаем URL
    detection_line_start = camera_config.get("detection_line_start", (0, 0.68))
    detection_line_end = camera_config.get("detection_line_end", (1.0, 0.35))
    
    if camera_url:
        success, image_path = capture_image(camera_name)

        if success:
            processed_image_path = process_image(image_path, camera_name, detection_line_start, detection_line_end)
            image = FSInputFile(processed_image_path)
            await callback_query.message.answer_photo(
                image,
                caption=f"Вот изображение с {CAMERAS[camera_name]['title']} с распознанными объектами!"
            )
        else:
            await callback_query.message.answer(f"Не удалось захватить изображение с {CAMERAS[camera_name]['title']}.")
    else:
        await callback_query.message.answer(f"Неизвестная камера: {CAMERAS[camera_name]['title']}.")

def register_handlers(dp: Dispatcher):
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(send_camera_options, Command("capture"))
    dp.callback_query.register(handle_camera_choice, CameraCallback.filter())
