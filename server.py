import os
import logging

from aiogram import Bot, Dispatcher, executor, types
import aiohttp

from categories import Categories
import exceptions
import expenses


logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")
PROXY_AUTH = aiohttp.BasicAuth(
    login=os.getenv("TELEGRAM_PROXY_LOGIN"),
    password=os.getenv("TELEGRAM_PROXY_PASSWORD")
)

bot = Bot(token=API_TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
dp = Dispatcher(bot)


def auth(func):

    async def wrapper(message):
        if message['from']['id'] != 135637452:
            return await message.reply("Access Denied", reply=False)
        return await func(message)

    return wrapper


@dp.message_handler(commands=['start', 'help'])
@auth
async def send_welcome(message: types.Message):
    await message.reply(
        "Бот для учёта финансов\n\n"
        "Добавить расход: 250 такси\n"
        "Сегодняшняя статистика: /today\n"
        "За текущий месяц: /month\n"
        "Последние внесённые расходы: /expenses\n"
        "Категории трат: /categories",
        reply=False)


@dp.message_handler(commands=['categories'])
@auth
async def categories_list(message: types.Message):
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n* " +\
            ("\n* ".join([c["name"]+' ('+", ".join(c["aliases"])+')' for c in categories]))
    await message.reply(answer_message, reply=False)


@dp.message_handler(commands=['today'])
@auth
async def today_statistics(message: types.Message):
    answer_message = expenses.get_today_statistics()
    await message.reply(answer_message, reply=False)


@dp.message_handler(commands=['month'])
@auth
async def month_statistics(message: types.Message):
    answer_message = expenses.get_month_statistics()
    await message.reply(answer_message, reply=False)


@dp.message_handler(commands=['expenses'])
@auth
async def list_expenses(message: types.Message):
    last_expenses = expenses.last()
    if not last_expenses:
        await message.reply("Расходы ещё не заведены", reply=False)
        return

    last_expenses_rows = [
        f"{row['amount']} руб. на {row['category_name']} —  нажми "
        f"/del{row['id']} для удаления"
        for row in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* ".join(last_expenses_rows)
    await message.reply(answer_message, reply=False)


@dp.message_handler(lambda message: message.text.startswith('/del'))
@auth
async def del_expense(message: types.Message):
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = "Удалил"
    await message.reply(answer_message, reply=False)


@dp.message_handler()
@auth
async def add_expense(message: types.Message):
    try:
        expense = expenses.add_expense(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.reply(str(e), reply=False)
        return
    answer_message = (
        f"Добавлены траты {expense.amount} руб на {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics()}")
    await message.reply(answer_message, reply=False)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
