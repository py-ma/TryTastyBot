# -*- coding: utf-8 -*-

"""bot's main file"""

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import markups
import config
import psycopg2

ORDER_DATA = {}

connection = psycopg2.connect(host='localhost', port='5433',
dbname='database', user='postgres', password = "imaster4")
cursor = connection.cursor()
cursor.execute("SELECT * from pizza")

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)
ORDER_DATA = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, f"Привет, {message.from_user.full_name}! "
    f"Хочешь заказать пиццу? Пиши команду /menu")

@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    request = cursor.fetchall()
    for name, description, price, photo in request:
        await bot.send_message(message.from_user.id, f"{name}\n\n" + f"{description}" + '[.]' + '(' + f"{photo}" + ')'
              + "\n\nЦена: " + price + " $",
                           parse_mode='markdown')

    return await bot.send_message(message.from_user.id, 'Выбери пиццу',
                                  reply_markup=markups.menu)

async def choose_size(message: types.Message):
    return await bot.send_message(message.from_user.id, 'Выбери размер',
                                  reply_markup=markups.size)

async def choose_dought(message: types.Message):
    return await bot.send_message(message.from_user.id, 'Выбери толщину теста',
                                  reply_markup=markups.dought)

async def user_address(message: types.Message):
    await bot.send_message(message.from_user.id, 'Напиши адрес для доставки')
    return await bot.send_document(message.from_user.id, open("addresses.txt", 'rb'))

async def repeat_order(message: types.Message):
    global position, size, dought, address
    position = ORDER_DATA[str(message.from_user.id)]['position']
    size = ORDER_DATA[str(message.from_user.id)]['size'].lower()
    dought = ORDER_DATA[str(message.from_user.id)]['dought'].lower()
    address = ORDER_DATA[str(message.from_user.id)]['address']
    return await bot.send_message(message.from_user.id,'Повторяю твой заказ... Верно?\n'
    f'{position}\nРазмер: {size}\nТесто: {dought}\nАдрес: {address}', reply_markup=markups.current)

async def create_pay(message: types.Message):
    from pyqiwip2p import QiwiP2P
    from config import SECRET_KEY
    p2p = QiwiP2P(auth_key=SECRET_KEY)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    r = f"SELECT price FROM pizza WHERE name = '{pizza}';"
    cursor.execute(r)
    re = cursor.fetchone()
    summa = re[0]
    new_bill = p2p.bill(amount=summa, lifetime=3)

    @dp.callback_query_handler(text="check")
    async def checking(callback: types.CallbackQuery):
        await callback.message.answer(f"Статус вашего платежа — {p2p.check(new_bill).status}")
        if p2p.check(new_bill).status == 'PAID':
            await bot.send_message(message.from_user.id, f"Оплачено!\nВаш заказ отправлен на кухню\nТы можешь заказать ещё, нажав /start")
            await bot.send_message("1154744059", 'Новый заказ!\n'
                                                 f'{position}\nРазмер: {size}\nТесто: {dought}\nАдрес: {address}')
        else:
            p2p.reject(bill_id=new_bill.bill_id)
            await bot.send_message(message.from_user.id, f"Не получилось! Ты можешь попробовать еще раз, нажав /start")
    link, check = InlineKeyboardButton("ссылка", url=new_bill.pay_url, callback_data='link'), InlineKeyboardButton('проверить оплату', callback_data='check')
    keyboard = InlineKeyboardMarkup().add(link, check)
    await bot.send_message(message.from_user.id, f"Держи ссылку на оплату твоего заказа", reply_markup=keyboard)

@dp.message_handler()
async def waiting(message: types.Message):
    names = f"select name from pizza;"
    cursor.execute(names)
    request = cursor.fetchall()
    if message.text in [e for l in request for e in l]:
        global pizza
        pizza = str(message.text)
        ORDER_DATA[str(message.from_user.id)] = {}
        ORDER_DATA[str(message.from_user.id)]['position'] = pizza
        return await choose_size(message)

    elif message.text in ('Большая', 'Маленькая'):
        ORDER_DATA[str(message.from_user.id)]['size'] = message.text
        return await choose_dought(message)

    elif message.text in ('Тонкое', 'Традиционное'):
        ORDER_DATA[str(message.from_user.id)]['dought'] = message.text
        return await user_address(message)

    addresses = f"select * from addresses;"
    cursor.execute(addresses)
    requestt = cursor.fetchall()
    if message.text in [e for l in requestt for e in l]:
        ORDER_DATA[str(message.from_user.id)]['address'] = message.text
        return await repeat_order(message)

    elif message.text == 'Верно':
        return await create_pay(message)

    elif message.text == 'Нет':
        await bot.send_message(message.from_user.id, 'Ну что же, давай по-новой')

    else:
        return await bot.send_message(message.from_user.id, 'Не понимаю тебя :(\nВыбери кнопку из меню')

if __name__ == '__main__':
    executor.start_polling(dp)
