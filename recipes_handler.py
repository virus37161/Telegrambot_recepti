import aiohttp
from token_data import OPEN_TOKEN
from datetime import datetime
from aiogram import F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.formatting import (
   Bold, as_list, as_marked_section
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types
from aiogram.filters import Command


class Order(StatesGroup):
    waiting_recept = State()
router = Router()

@router.message(Command("category_search_random"))
async def category(message: Message, state: FSMContext, command:CommandObject):
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(url = f"http://www.themealdb.com/api/json/v1/1/categories.php") as resp:
            cat = await resp.json()
        kb1 = ReplyKeyboardBuilder()
        for i in cat.get("categories"):
            kb1.add(types.KeyboardButton(text=f"{i.get('strCategory')}"))
        kb1.adjust(2)
    await message.answer(f'Выберите категорию:', reply_markup=kb1.as_markup(resize_keybord=True))
    await state.set_state(Order.waiting_recept.state)

@router.message(Order.waiting_recept)
async def recipes(message: types.Message, state: FSMContext):
    await message.answer(f"{message.text}")
