import asyncio

import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
from aiogram.utils.formatting import (
   Bold, as_list, as_marked_section
)

from token_data import TOKEN
from recipes_handler import router

dp = Dispatcher()
dp.include_router(router)
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = [[types.KeyboardButton(text="Команды"), types.KeyboardButton(text= "Описание бота")],]
    keybord = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,)
    await message.answer(f'Привет! С чего начнем?', reply_markup=keybord)


@dp.message(F.text.lower() == "команды")
async def commands(message: types.Message):
    responce = as_list(as_marked_section(Bold("Команды:"), "/category_search_random + количество желаемых рецептов  --  /получить все категории и количество рецептов данной категории. \nПример: /category_search_random 4", marker="✅"),)
    await message.answer(**responce.as_kwargs())









async def main() -> None:
   bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
   await dp.start_polling(bot)

if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO, stream=sys.stdout)
   asyncio.run(main())
