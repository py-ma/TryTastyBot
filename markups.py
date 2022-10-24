# -*- coding: utf-8 -*-

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

Margarita = KeyboardButton('Маргарита')
Mushroom = KeyboardButton('Грибная')
Pepperoni = KeyboardButton('Пепперони')
Caprichosa = KeyboardButton('Капричоза')
Greek = KeyboardButton('Греческая')
menu = ReplyKeyboardMarkup(resize_keyboard=True).add(Margarita, Mushroom, Pepperoni, Caprichosa, Greek)

Big = KeyboardButton('Большая')
Small = KeyboardButton('Маленькая')
size = ReplyKeyboardMarkup(resize_keyboard=True).add(Big, Small)

Thin = KeyboardButton('Тонкое')
Traditional = KeyboardButton('Традиционное')
dought = ReplyKeyboardMarkup(resize_keyboard=True).add(Thin, Traditional)

Yes = KeyboardButton('Верно')
No = KeyboardButton('Нет')
current = ReplyKeyboardMarkup(resize_keyboard=True).add(Yes, No)

