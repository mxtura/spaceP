from aiogram import types, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from bot.utils import capture_image, clear_images_dir

def register_handlers(dp: Dispatcher):
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(capture_and_send_image, Command("capture"))

async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, который отправляет кадр парковочного места. Отправь мне команду /capture, чтобы получить изображение парковки с воказала БВ.")

async def capture_and_send_image(message: types.Message):
    await message.reply("Пожалуйста, подождите, идет захват изображения...")
    
    clear_images_dir()

    # Запускаем функцию захвата изображения с помощью Selenium
    success, image_path = capture_image()
    print(image_path)

    if success:
        
        # Отправляем изображение пользователю
        image = FSInputFile(image_path)
        
        await message.answer_photo(image, caption="Вот ваше изображение с камеры!")
    else:
        await message.reply("Не удалось захватить изображение.")
