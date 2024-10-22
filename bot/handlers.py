from aiogram import types, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from bot.utils import capture_image, clear_images_dir, process_image

def register_handlers(dp: Dispatcher):
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(capture_and_send_image, Command("capture"))

async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, который отправляет кадр парковочного места. Отправь мне команду /capture, чтобы получить изображение парковки с воказала БВ.")

async def capture_and_send_image(message: types.Message):
    await message.reply("Пожалуйста, подождите, идет захват изображения...")

    clear_images_dir()

    # Захват изображения с камеры
    success, image_path = capture_image()

    if success:
        # Обработка изображения через YOLO
        processed_image_path = process_image(image_path)
        
        # Отправляем обработанное изображение пользователю
        image = FSInputFile(processed_image_path)
        await message.answer_photo(image, caption="Вот изображение с распознанными объектами!")
    else:
        await message.reply("Не удалось захватить изображение.")
