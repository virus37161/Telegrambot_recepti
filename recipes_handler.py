import aiohttp
import asyncio

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
import random

from googletrans import Translator
translator= Translator()

class Order(StatesGroup):
    waiting_menu = State()
    waiting_recepies = State()
router = Router()

@router.message(Command("category_search_random"))
async def category(message: Message, state: FSMContext, command:CommandObject):
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return
    try:
        s =int(command.args)
    except ValueError as e:
        await message.answer("Необходимо ввести цифровое значение")
        return
    await state.set_data([int(command.args)])
    async with aiohttp.ClientSession() as session:
        async with session.get(url = f"http://www.themealdb.com/api/json/v1/1/categories.php") as resp:
            cat = await resp.json()
        kb1 = ReplyKeyboardBuilder()
        for i in cat.get("categories"):
            kb1.add(types.KeyboardButton(text=f"{i.get('strCategory')}"))
        kb1.adjust(2)
    await message.answer(f'Выберите категорию:', reply_markup=kb1.as_markup(resize_keybord=True))
    await state.set_state(Order.waiting_menu.state)

@router.message(Order.waiting_menu)
async def recipes(message: types.Message, state: FSMContext):
    col = await state.get_data()
    async with aiohttp.ClientSession() as session:
        async with session.get(url = f"http://www.themealdb.com/api/json/v1/1/filter.php?c={message.text}") as resp:
            log = await resp.json()
            if  col[0] > len(log.get("meals")):
                await message.answer(f"Максимальное количество рецептов для категории {message.text} - {len(log.get('meals'))}")
                return
            choice = []
            id ={}
            for i in log['meals']:
                choice.append(i.get('strMeal'))
                id[i.get('strMeal')] = i.get('idMeal')
            choice = random.sample(choice, k=col[0])
            choice_dict= {}
            for i in choice:
                choice_dict[i]= id.get(i)
            await state.set_data([choice_dict])
            choice_russian = []
            for i in choice:
                rus = translator.translate(i, dest = "ru")
                choice_russian.append(rus.text)
            choice = as_list(as_marked_section(Bold("Вот ваши рецепты:"), *choice_russian, marker="✅"))
    kb1 = ReplyKeyboardBuilder()
    kb1.add(types.KeyboardButton(text="Показать рецепты"))
    await message.answer(**choice.as_kwargs(), reply_markup=kb1.as_markup(resize_keybord=True))
    await state.set_state(Order.waiting_recepies.state)

async def look_for(t):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"http://www.themealdb.com/api/json/v1/1/lookup.php?i={int(t)}") as resp:
            log = await resp.json()
    ingredient = []
    n = 1
    while log.get("meals")[0].get(f"strIngredient{n}") != "":
        ingredient.append(log.get("meals")[0].get(f"strIngredient{n}"))
        n+=1
    a = {"strMeal":log.get("meals")[0].get("strMeal"), "strInstractions": log.get("meals")[0].get("strInstructions"), "ingredient": ingredient}
    return a

@router.message(Order.waiting_recepies)
async def recipes(message:types.Message, state:FSMContext):
    logger= await state.get_data()
    s=[]
    for i, f in logger[0].items():
        s.append(look_for(f))
        print(f)
    b = await asyncio.gather(*s)
    for i in b:
        s = i.get('ingredient')
        s = ', '.join(s)
        ingredientss = translator.translate(s, dest ="ru").text
        instraction = i.get('strInstractions')
        instraction = translator.translate(instraction, dest = 'ru').text
        name = i.get('strMeal')
        name = translator.translate(name, dest ='ru').text
        recept = as_list(as_marked_section(Bold(f"Блюдо: {name}"), f"\nРецепт: \n \n{instraction}", f"\nИнгредиенты:\n\n{ingredientss}", marker=""))
        await message.answer (**recept.as_kwargs())
        
