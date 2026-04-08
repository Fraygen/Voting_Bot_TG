from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Начать голосование",
                         callback_data="start voting")]
])

voting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Дальше", callback_data="next")],
    [InlineKeyboardButton(text="Назад", callback_data="prev")],
    [InlineKeyboardButton(text="Голосовать", callback_data="vote")]
])

last = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="prev")],
    [InlineKeyboardButton(text="Главное меню", callback_data="home")]
])

cancel_vote = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗑️ Отменить голос", callback_data="cancel_vote")]
])

new_vote = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗳️ Голосовать заново", callback_data="start voting")]
])

sure = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, отменить голос", callback_data="del")],
    [InlineKeyboardButton(text="❌ Нет, оставить голос", callback_data="finish")]
])

after_vote = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Готово", callback_data="finish")],
    [InlineKeyboardButton(text="🗑️ Отменить голос", callback_data="cancel_vote")]
])