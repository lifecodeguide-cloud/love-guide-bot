import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "YOUR_TOKEN"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(lambda message: message.text == "/start")
async def start_handler(message: types.Message):
    await message.answer(
        "Это раздел совместимости 💞\n\nНажми дальше:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Дальше ➡️", callback_data="next")]
            ]
        )
    )

@dp.callback_query(lambda c: c.data == "next")
async def next_handler(callback: types.CallbackQuery):
    await callback.message.answer("Скоро здесь будет разбор совместимости ✨")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
