# ---------------------------------------ПОДКЛЮЧЕННЫЕ БИБЛИОТЕКИ------------------------------------------

import io  # библиотека для работы с оперативной памятью
import logging  # библиотека для логов
import re  # библиотека для работы со строками
import asyncio  # библиотека для постоянно повторяющегося прохода по алертам
import datetime  # библиотека для получения даты
import random  # библиотека для получения случайного числа

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP  # измененная библиотека telegram - календаря
from aiogram import Bot, Dispatcher, executor, types  # библиотека для работы с телеграмом
from aiogram.dispatcher.filters.state import State, StatesGroup  # машина состояний
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # управление памятью
from aiogram.dispatcher import FSMContext  # машина состояний
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import requests.packages.urllib3  # её я использовал для того, чтобы "небезопасные" запросы в finviz работали

# -----------------------------------------ПОДКЛЮЧЕННЫЕ ФАЙЛЫ---------------------------------------------


import messages  # файл со стандартными сообщениями
import keyboards as kb  # файл с клавиатурами
import plot  # файл с функциями для построения графиков
import settings  # файл с настройками
import sm_info as sm  # файл с функциями, связанными с биржей
from db_manipulator import Database  # файл, отвечающий за работу с базами данных
import mail  # файл с функциями, отвечающими за почту
import date  # модифицированная версия datetime
import tickers  # файл с тикерами

# -------------------------------------------ИНИЦИАЛИЗАЦИЯ------------------------------------------------


requests.packages.urllib3.disable_warnings()  # это нужно для того, чтобы библиотека Finviz работала нормально

# задаём уровень логов
logging.basicConfig(level=logging.INFO)

# инициализация соединения с БД
db = Database('users.db')

# инициализация бота и памяти для машины состояний
storage = MemoryStorage()
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

# ---------------------------------ПЕРЕМЕННЫЕ ДЛЯ РАБОТЫ НЕКОТОРЫХ ФУНКЦИЙ--------------------------------


code = ""  # сюда сохраняется код для подтверждения электронной почты
i = 0  # это счётчик неудачных попыток ввода кода, присланного на почту
active_id = 0  # это id активного алерта для изменения


# --------------------------------------ПОДКЛЮЧЕНИЕ МАШИНЫ СОСТОЯНИЙ--------------------------------------


# состояние для получения информации о ценной бумаге
class Info(StatesGroup):
    receive_ticker = State()


# состояния для записи нового алерта
class AddAlert(StatesGroup):
    ticker = State()
    mode = State()
    value = State()
    message = State()
    time = State()
    accept = State()


# состояния для редактирования активного алерта
class EditAlert(StatesGroup):
    edit_ticker = State()
    edit_mode = State()
    edit_value = State()
    edit_message = State()
    edit_time = State()
    delete_alert = State()


# состояние для записи обратной связи
class Feedback(StatesGroup):
    fb = State()


# состояния для добавления или изменения адреса электронной почты
class EmailChange(StatesGroup):
    email = State()
    check = State()


# состояние для добавления инвестиционного портфеля
class AddPortfolio(StatesGroup):
    name = State()


# состояния для редактирования портфеля
class EditPortfolio(StatesGroup):
    delete_portfolio = State()


# состояния для добавления ценной бумаги в портфель
class AddStock(StatesGroup):
    ticker = State()
    value = State()
    currency = State()
    accept = State()


# состояния для удаления ценной бумаги из портфеля
class DelStock(StatesGroup):
    ticker = State()
    value = State()
    currency = State()
    accept = State()


# состояния для добавления денег в портфель
class AddMoney(StatesGroup):
    wallet = State()
    value = State()
    accept = State()


# состояния для удаления денег из ортфеля
class DelMoney(StatesGroup):
    wallet = State()
    value = State()
    accept = State()

# ------------------------------------------ОБРАБОТЧИКИ КОМАНД----------------------------------------------


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.message, state: FSMContext):
    await bot.send_message(message.from_user.id, messages.description, parse_mode='HTML')
    await bot.send_message(message.from_user.id, messages.main_menu, reply_markup=kb.mainMenu)
    await state.finish()


# -------------------------------------------ОБРАТНАЯ СВЯЗЬ-------------------------------------------------


# обработчик состояния "Обратная связь"
@dp.message_handler(state=Feedback.fb, content_types=types.ContentTypes.TEXT)
async def alert_get_message(message: types.Message, state: FSMContext):
    await state.update_data(fb=message.text)
    fb_data = await state.get_data()
    await bot.send_message(settings.owner, "Сообщение от пользователя " + str(message.from_user.id) +
                           ": " + str(fb_data['fb']))
    await bot.send_message(message.from_user.id, messages.main_menu, reply_markup=kb.mainMenu)
    await state.finish()


# обработчик кнопки "вернуться в главное меню" для обратной связи
@dp.callback_query_handler(lambda call: True, state=Feedback.fb)
async def back_to_main_menu(call, state: FSMContext):
    if call.data == "main_menu_button":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.main_menu, reply_markup=kb.mainMenu)
        await state.finish()


# --------------------------------------ПОЛУЧЕНИЕ ИНФОРМАЦИИ О БУМАГЕ-------------------------------------


@dp.message_handler(state=Info.receive_ticker, content_types=types.ContentTypes.TEXT)
async def receive_ticker_info(message: types.Message, state: FSMContext):
    if not sm.ticker_exists(message.text.upper()):
        await bot.send_message(message.from_user.id, messages.ticker_not_exists)
        return
    await bot.send_message(message.from_user.id, messages.ticker_info(message.text.upper()),
                           reply_markup=kb.standart_kb, parse_mode='HTML')
    await state.finish()


# -------------------------------------ОБРАБОТЧИКИ КНОПОК БЕЗ СОСТОЯНИЯ-----------------------------------


@dp.callback_query_handler(lambda call: True)
async def callback_inline(call):
    global active_id
    # главное меню
    if call.data == "my_portfolios":
        # media = [InputMediaPhoto(io.BufferedReader(plot.pie([10, 5, 9], ["fewf", "fqwef", "fqefq"], "wfew"))),
        #         InputMediaPhoto(io.BufferedReader(plot.pie([30, 40, 50], ["fedsadf", "fqddd", "faaa"], "sdsakmk"))),
        #         InputMediaPhoto(io.BufferedReader(plot.pie([3, 6, 1], ["осм назв", "авы", "ыфйъ"], "выфвыфw")))]
        # await bot.send_media_group(call.message.chat.id, media)
        # media.clear()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.my_portfolios(call.message.chat.id), parse_mode='HTML',
                                    reply_markup=kb.my_portfolios_menu)
    if call.data == "info":
        await Info.receive_ticker.set()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML',
                                    text="Введите тикер для получения информации о бумаге:\n\n*Если тикер принадлежит "
                                         "европейской бирже, введите её название через точку (Например, ADS.DE)")
    if call.data == "alerts":
        kb.active_alerts = InlineKeyboardButton('Активные алерты [' +
                                                str(len(db.active_alerts_list(call.message.chat.id))) +
                                                ']', callback_data='active_alerts')
        kb.executed_alerts = InlineKeyboardButton('Выполненные алерты [' +
                                                  str(len(db.executed_alerts_list(call.message.chat.id))) +
                                                  ']', callback_data='executed_alerts')
        kb.alMenu = InlineKeyboardMarkup(row_width=1).add(kb.active_alerts, kb.executed_alerts, kb.add_alert,
                                                          kb.backToMainMenu)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.alerts, parse_mode='HTML',
                                    reply_markup=kb.alMenu)
    if call.data == "feedback":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.feedback, reply_markup=kb.feedback_menu)
        await Feedback.fb.set()
    if call.data == "settings":
        await change_settings_keyboard(call.message.chat.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.settings_menu(call.message.chat.id),
                                    reply_markup=kb.settings_menu, parse_mode="HTML")

    # меню инвестиционных портфелей
    if call.data == "add_portfolio":
        await bot.send_message(call.message.chat.id, "Введите название портфеля: ")
        await AddPortfolio.name.set()
    if call.data == "add_stock":
        await bot.send_message(call.message.chat.id, "Введите тикер:")
        await AddStock.ticker.set()
    if call.data == "del_stock":
        if db.portfolio_has_stocks(call.message.chat.id, active_id):
            await bot.send_message(call.message.chat.id, "Выберите тикер:")
            await DelStock.ticker.set()
    if call.data == "add_money":
        await bot.send_message(call.message.chat.id, "Выберите валюту:", reply_markup=kb.wallet_menu)
        await AddMoney.wallet.set()
    if call.data == "del_money":
        await bot.send_message(call.message.chat.id, "Выберите валюту:", reply_markup=kb.adaptive_wallet_keyboard(
                db.money_wallets_in_portfolio(call.message.chat.id, active_id)))
        await DelMoney.wallet.set()
    if call.data == "delete_portfolio":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.portfolio_full_info(call.message.chat.id, active_id) +
                                         "\n--------------------\n\n" + "Вы уверены, что хотите удалить портфель?",
                                    parse_mode='HTML', reply_markup=kb.delete_menu)
        await EditPortfolio.delete_portfolio.set()

    # меню алертов
    if call.data == "active_alerts":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.active_alerts(call.message.chat.id), parse_mode="HTML",
                                    reply_markup=kb.univAlMenu)
    if call.data == "executed_alerts":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.deactive_alerts(call.message.chat.id), parse_mode="HTML",
                                    reply_markup=kb.univAlMenu)
    if call.data == "add_alert":
        await bot.send_message(call.message.chat.id, messages.add_alert_first_step)
        await AddAlert.ticker.set()

    # редактирование алерта
    if call.data == "edit_ticker":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.add_alert_first_step)
        await EditAlert.edit_ticker.set()
    if call.data == "edit_mode_and_value":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выберите режим алерта", reply_markup=kb.mode_select)
        await EditAlert.edit_mode.set()
    if call.data == "edit_time":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выберите тип алерта:", parse_mode="HTML",
                                    reply_markup=kb.time_menu)
        await EditAlert.edit_time.set()
    if call.data == "edit_message":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Введите текст алерта")
        await EditAlert.edit_message.set()
    if call.data == "delete_alert":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.alert_full_info(call.message.chat.id, active_id) +
                                         "\n--------------------\n\n" + "Вы уверены, что хотите удалить алерт?",
                                    parse_mode='HTML', reply_markup=kb.delete_menu)
        await EditAlert.delete_alert.set()
    if call.data == "off_alert":
        db.alert_off(call.message.chat.id, active_id)
        kb.active_alerts = InlineKeyboardButton('Активные алерты [' +
                                                str(len(db.active_alerts_list(call.message.chat.id))) +
                                                ']', callback_data='active_alerts')
        kb.executed_alerts = InlineKeyboardButton('Выполненные алерты [' +
                                                  str(len(db.executed_alerts_list(call.message.chat.id))) + ']',
                                                  callback_data='executed_alerts')
        kb.alMenu = InlineKeyboardMarkup(row_width=1).add(kb.active_alerts, kb.executed_alerts
                                                          , kb.add_alert,
                                                          kb.backToMainMenu)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.alerts, reply_markup=kb.alMenu)
    if call.data == "reactivate_alert":
        db.activate_alert_by_id(call.message.chat.id, active_id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.deactive_alerts(call.message.chat.id), parse_mode="HTML",
                                    reply_markup=kb.univAlMenu)

    # кнопка "главное меню"
    if call.data == "main_menu_button":
        await bot.send_message(chat_id=call.message.chat.id, text=messages.description, parse_mode='HTML')
        await bot.send_message(chat_id=call.message.chat.id, text=messages.main_menu, reply_markup=kb.mainMenu)

    # добавление почты
    if call.data == "add_mail":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.email_enter,
                                    reply_markup=kb.toSettings)
        await EmailChange.email.set()

    # изменение состояния "дублировать алерты на электронную почту
    if call.data == "mail_alert":
        if db.mail_exists(call.message.chat.id) and not db.user_exists(call.message.chat.id):
            db.add_user(call.message.chat.id)
            await change_settings_keyboard(call.message.chat.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=messages.settings_menu(call.message.chat.id),
                                        reply_markup=kb.settings_menu, parse_mode="HTML")
        elif db.mail_exists(call.message.chat.id) and db.is_on_email_alert(call.message.chat.id):
            db.alert_mail_off(call.message.chat.id)
            await change_settings_keyboard(call.message.chat.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=messages.settings_menu(call.message.chat.id),
                                        reply_markup=kb.settings_menu, parse_mode="HTML")
        elif db.mail_exists(call.message.chat.id) and not db.is_on_email_alert(call.message.chat.id):
            db.alert_mail_on(call.message.chat.id)
            await change_settings_keyboard(call.message.chat.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=messages.settings_menu(call.message.chat.id),
                                        reply_markup=kb.settings_menu, parse_mode="HTML")


# ----------------------------------------ДОБАВЛЕНИЕ НОВОГО ПОРТФЕЛЯ--------------------------------------


# получение названия портфеля
@dp.message_handler(state=AddPortfolio.name, content_types=types.ContentTypes.TEXT)
async def portfolio_name(message: types.Message, state: FSMContext):
    global active_id
    if db.portfolio_name_exists(message.from_user.id, message.text):
        await bot.send_message(message.from_user.id, "Портфель с таким названием уже существует")
        return
    db.add_portfolio(message.from_user.id, message.text)
    await bot.send_message(message.from_user.id, "Портфель добавлен")
    await bot.send_message(chat_id=message.from_user.id, text=messages.my_portfolios(message.from_user.id),
                           parse_mode='HTML', reply_markup=kb.my_portfolios_menu)
    await state.finish()


# -------------------------------------------ДОБАВЛЕНИЕ ДЕНЕГ В ПОРТФЕЛЬ----------------------------------


# получение валюты
@dp.callback_query_handler(lambda call: True, state=AddMoney.wallet)
async def accept_new_stock(call, state: FSMContext):
    if call.data == "usd_wallet":
        await state.update_data(wallet="USD")
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выбрана валюта USD")
        await bot.send_message(call.message.chat.id, "Введите количество: ")
        await AddMoney.next()
    if call.data == "rub_wallet":
        await state.update_data(wallet="RUB")
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выбрана валюта RUB")
        await bot.send_message(call.message.chat.id, "Введите количество: ")
        await AddMoney.next()
    if call.data == "eur_wallet":
        await state.update_data(wallet="EUR")
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выбрана валюта EUR")
        await bot.send_message(call.message.chat.id, "Введите количество: ")
        await AddMoney.next()


# получение количества
@dp.message_handler(state=AddMoney.value, content_types=types.ContentTypes.TEXT)
async def new_stock_ticker(message: types.Message, state: FSMContext):
    value = sm.try_float(message.text)
    if not value or (message.text.isdigit() and (int(message.text) < 0)):
        await bot.send_message(message.from_user.id, "Введите корректное значение")
        return
    await state.update_data(value=value)
    money_data = await state.get_data()
    await bot.send_message(message.from_user.id,
                           f"<u><b>Внесение денег:</b></u>\n\n<b>Валюта: </b>{money_data['wallet']}"
                           f"\n<b>Количество: </b>{money_data['value']}",
                           parse_mode="HTML", reply_markup=kb.money_accept_menu)
    await AddMoney.next()


# отмена или добавление денег в БД
@dp.callback_query_handler(lambda call: True, state=AddMoney.accept)
async def accept_new_stock(call, state: FSMContext):
    if call.data == "accept":
        money_data = await state.get_data()
        db.add_money(call.message.chat.id, active_id, money_data['wallet'], money_data['value'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Валюта внесена")
        await bot.send_message(call.message.chat.id, messages.portfolio_full_info(call.message.chat.id, active_id),
                               reply_markup=kb.edit_portfolio_menu, parse_mode='HTML')

        await state.finish()
    if call.data == "cancel":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Внесение валюты отменено")
        await bot.send_message(call.message.chat.id, messages.portfolio_full_info(call.message.chat.id, active_id),
                               reply_markup=kb.edit_portfolio_menu, parse_mode='HTML')
        await state.finish()
    if call.data == "edit_stock":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Ввыберите валюту:", reply_markup=kb.wallet_menu)
        await AddMoney.first()


# -------------------------------------------ВЫВОД ДЕНЕГ ИЗ ПОРТФЕЛЯ--------------------------------------


# получение валюты
@dp.callback_query_handler(lambda call: True, state=DelMoney.wallet)
async def accept_new_stock(call, state: FSMContext):
    if call.data == "usd_wallet":
        await state.update_data(wallet="USD")
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выбрана валюта USD")
        await bot.send_message(call.message.chat.id, "Введите количество: ")
        await DelMoney.next()
    if call.data == "rub_wallet":
        await state.update_data(wallet="RUB")
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выбрана валюта RUB")
        await bot.send_message(call.message.chat.id, "Введите количество: ")
        await DelMoney.next()
    if call.data == "eur_wallet":
        await state.update_data(wallet="EUR")
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выбрана валюта EUR")
        data = await state.get_data()
        await bot.send_message(call.message.chat.id, f"Введите количество (максимум {round(db.number_of_money_in_portfolio(call.message.chat.id, active_id, data['wallet']),2)}):")
        await DelMoney.next()


# получение количества
@dp.message_handler(state=DelMoney.value, content_types=types.ContentTypes.TEXT)
async def new_stock_ticker(message: types.Message, state: FSMContext):
    value = sm.try_float(message.text)
    if not value or (message.text.isdigit() and (int(message.text) < 0)):
        await bot.send_message(message.from_user.id, "Введите корректное значение")
        return
    await state.update_data(value=value)
    money_data = await state.get_data()
    await bot.send_message(message.from_user.id,
                           f"<u><b>Вывод денег:</b></u>\n\n<b>Валюта: </b>{money_data['wallet']}"
                           f"\n<b>Количество: </b>{money_data['value']}",
                           parse_mode="HTML", reply_markup=kb.money_accept_menu)
    await DelMoney.next()


# отмена или добавление денег в БД
@dp.callback_query_handler(lambda call: True, state=DelMoney.accept)
async def accept_new_stock(call, state: FSMContext):
    if call.data == "accept":
        money_data = await state.get_data()
        db.del_money(call.message.chat.id, active_id, money_data['wallet'], money_data['value'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Деньги выведены")
        await bot.send_message(call.message.chat.id, messages.portfolio_full_info(call.message.chat.id, active_id),
                               reply_markup=kb.edit_portfolio_menu, parse_mode='HTML')

        await state.finish()
    if call.data == "cancel":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выведение денег отменено")
        await bot.send_message(call.message.chat.id, messages.portfolio_full_info(call.message.chat.id, active_id),
                               reply_markup=kb.edit_portfolio_menu, parse_mode='HTML')
        await state.finish()
    if call.data == "edit_stock":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Выберите валюту:", reply_markup=kb.wallet_menu)
        await DelMoney.first()


# --------------------------------------ДОБАВЛЕНИЕ ЦЕННОЙ БУМАГИ В ПОРТФЕЛЬ-------------------------------


# получение тикера
@dp.message_handler(state=AddStock.ticker, content_types=types.ContentTypes.TEXT)
async def new_stock_ticker(message: types.Message, state: FSMContext):
    if not sm.ticker_exists(message.text.upper()):
        await bot.send_message(message.from_user.id, messages.ticker_not_exists)
        return
    await state.update_data(ticker=message.text)
    await AddStock.next()
    await bot.send_message(message.from_user.id, "Введите количество бумаг: ")


# получение количества бумаг
@dp.message_handler(state=AddStock.value, content_types=types.ContentTypes.TEXT)
async def new_stock_quantity(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or (message.text.isdigit() and (int(message.text) < 0)):
        await bot.send_message(message.from_user.id, "Введите корректное значение")
        return
    await state.update_data(value=message.text)
    data = await state.get_data()
    await AddStock.next()
    await bot.send_message(message.from_user.id, f"Введите цену за одну бумагу ({sm.wallet(data['ticker'])}): ")


# получение цены за бумагу
@dp.message_handler(state=AddStock.currency, content_types=types.ContentTypes.TEXT)
async def new_stock_value(message: types.Message, state: FSMContext):
    if not sm.try_float(message.text):
        await bot.send_message(message.from_user.id, "Введите корректное значение")
        return
    await state.update_data(currency=str(sm.try_float(message.text)))
    stock_data = await state.get_data()
    await bot.send_message(message.from_user.id,
                           f"<u><b>Покупка ценной бумаги:</b></u>\n\n<b>Тикер: </b>{stock_data['ticker']}"
                           f"\n<b>Количество: </b>{stock_data['value']}\n<b>Цена за бумагу: </b>"
                           f"{stock_data['currency']} {sm.wallet(stock_data['ticker'])}",
                           parse_mode="HTML", reply_markup=kb.stock_accept_menu)
    await AddStock.next()


# отмена или добавление ценной бумаги в БД
@dp.callback_query_handler(lambda call: True, state=AddStock.accept)
async def accept_new_stock(call, state: FSMContext):
    if call.data == "accept":
        stock_data = await state.get_data()
        db.add_stock(call.message.chat.id, active_id, stock_data['ticker'], stock_data['currency'], stock_data['value'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Бумага куплена")
        await bot.send_message(call.message.chat.id, messages.portfolio_full_info(call.message.chat.id, active_id),
                               reply_markup=kb.edit_portfolio_menu, parse_mode='HTML')

        await state.finish()
    if call.data == "cancel":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Покупка бумаги отменена")
        await bot.send_message(call.message.chat.id, messages.portfolio_full_info(call.message.chat.id, active_id),
                               reply_markup=kb.edit_portfolio_menu, parse_mode='HTML')
        await state.finish()
    if call.data == "edit_stock":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Введите тикер:")
        await AddStock.first()


# --------------------------------------УДАЛЕНИЕ ЦЕННОЙ БУМАГИ ИЗ ПОРТФЕЛЯ--------------------------------


# получение тикера
@dp.message_handler(state=DelStock.ticker, content_types=types.ContentTypes.TEXT)
async def new_stock_ticker(message: types.Message, state: FSMContext):
    if not db.ticker_exists_in_portfolio(message.from_user.id, active_id, ticker=message.text):
        await bot.send_message(message.from_user.id, "Введите тикер, который есть в портфеле:")
        return
    await state.update_data(ticker=message.text)
    await DelStock.next()
    await bot.send_message(message.from_user.id, f"Введите количество бумаг (максимум "
                                                 f"{round(db.number_of_stocks_in_portfolio(message.from_user.id, active_id, message.text),2)}): ")


# получение количества бумаг
@dp.message_handler(state=DelStock.value, content_types=types.ContentTypes.TEXT)
async def new_stock_quantity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not message.text.isdigit() or int(message.text) > int(
            db.number_of_stocks_in_portfolio(message.from_user.id, active_id,
                                             data['ticker'])) or (message.text.isdigit() and (int(message.text) < 0)):
        await bot.send_message(message.from_user.id, "Введите корректное значение")
        return
    await state.update_data(value=message.text)
    await DelStock.next()
    await bot.send_message(message.from_user.id, f"Введите цену за одну бумагу ({sm.wallet(data['ticker'])}): ")


# получение цены за бумагу
@dp.message_handler(state=DelStock.currency, content_types=types.ContentTypes.TEXT)
async def new_stock_value(message: types.Message, state: FSMContext):
    if not sm.try_float(message.text):
        await bot.send_message(message.from_user.id, "Введите корректное значение")
        return
    await state.update_data(currency=message.text)
    stock_data = await state.get_data()
    await bot.send_message(message.from_user.id,
                           f"<u><b>Продажа ценной бумаги:</b></u>\n\n<b>Тикер: </b>{stock_data['ticker']}"
                           f"\n<b>Количество: </b>{stock_data['value']}\n<b>Цена за бумагу: </b>"
                           f"{stock_data['currency']} {sm.wallet(stock_data['ticker'])}",
                           parse_mode="HTML", reply_markup=kb.stock_accept_menu)
    await DelStock.next()


# отмена или добавление ценной бумаги в БД
@dp.callback_query_handler(lambda call: True, state=DelStock.accept)
async def accept_new_stock(call, state: FSMContext):
    if call.data == "accept":
        stock_data = await state.get_data()
        db.del_stock(call.message.chat.id, active_id, stock_data['ticker'], stock_data['currency'], stock_data['value'])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Бумага продана")
        await bot.send_message(call.message.chat.id, messages.portfolio_full_info(call.message.chat.id, active_id),
                               reply_markup=kb.edit_portfolio_menu, parse_mode='HTML')

        await state.finish()
    if call.data == "cancel":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Продажа бумаги отменена")
        await bot.send_message(call.message.chat.id, messages.portfolio_full_info(call.message.chat.id, active_id),
                               reply_markup=kb.edit_portfolio_menu, parse_mode='HTML')
        await state.finish()
    if call.data == "edit_stock":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Введите тикер:")
        await DelStock.first()


# --------------------------------------------ДОБАВЛЕНИЕ АЛЕРТА-------------------------------------------


# получение тикера
@dp.message_handler(state=AddAlert.ticker, content_types=types.ContentTypes.TEXT)
async def alert_get_ticker(message: types.Message, state: FSMContext):
    if not sm.ticker_exists(message.text.upper()):
        await bot.send_message(message.from_user.id, messages.ticker_not_exists)
        return
    await state.update_data(ticker=message.text.upper())
    alert_data = await state.get_data()
    if alert_data['ticker'] in tickers.moex_tickers or "." in alert_data['ticker']:
        mode_select = InlineKeyboardMarkup(row_width=1).add(kb.reaching, kb.day_increase, kb.day_decrease,
                                                            kb.day_increase_percent, kb.day_decrease_percent)
        await AddAlert.next()
        await bot.send_message(message.from_user.id, "Выберите режим алерта", reply_markup=mode_select)
    else:
        await AddAlert.next()
        await bot.send_message(message.from_user.id, "Выберите режим алерта", reply_markup=kb.mode_select)


# получение режима алерта
@dp.callback_query_handler(lambda call: True, state=AddAlert.mode)
async def alert_get_mode(call, state: FSMContext):
    if call.data == "reaching":
        await state.update_data(mode=call.data)
        await AddAlert.next()
        alert = await state.get_data()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages.mode_message(str(alert['ticker'])))
    if call.data == "increased_vol":
        await state.update_data(mode=call.data)
        await AddAlert.next()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите процент увеличения от нормы:")
    if call.data == "day_increase":
        await state.update_data(mode=call.data)
        await AddAlert.next()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите значение увеличения цены внутри дня:")
    if call.data == "day_decrease":
        await state.update_data(mode=call.data)
        await AddAlert.next()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите значение уменьшения цены внутри дня:")
    if call.data == "day_increase_percent":
        await state.update_data(mode=call.data)
        await AddAlert.next()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите процент увеличения цены внутри дня:")
    if call.data == "day_decrease_percent":
        await state.update_data(mode=call.data)
        await AddAlert.next()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите процент уменьшения цены внутри дня:")


# получение значения
@dp.message_handler(state=AddAlert.value, content_types=types.ContentTypes.TEXT)
async def alert_get_value(message: types.Message, state: FSMContext):
    if not sm.is_value(message.text) or (sm.is_value(message.text) and int(int(message.text) < 0)):
        await bot.send_message(message.from_user.id, "Введите корректное значение")
        return
    await state.update_data(value=sm.make_value(message.text))
    await AddAlert.next()
    await bot.send_message(message.from_user.id, "Введите текст алерта")


# получение сообщения-ответа
@dp.message_handler(state=AddAlert.message, content_types=types.ContentTypes.TEXT)
async def alert_get_message(message: types.Message, state: FSMContext):
    await state.update_data(message=message.text)
    await bot.send_message(message.from_user.id, "Выберите тип алерта:", parse_mode="HTML", reply_markup=kb.time_menu)
    await AddAlert.next()


# инлайновый календарь
@dp.callback_query_handler(DetailedTelegramCalendar.func(), state=AddAlert.time)
async def inline_kb_answer_callback_handler(call, state: FSMContext):
    result, key, step = DetailedTelegramCalendar(current_date=datetime.datetime.now().today().date(),
                                                 min_date=datetime.datetime.now().today().date(),
                                                 locale='ru').process(call.data)
    a = ""
    if not result and key:
        if LSTEP[step] == "month":
            a = "месяц"
        elif LSTEP[step] == "day":
            a = "день"
        await bot.edit_message_text(f"Выберите {a}",
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=key)
    elif result:
        mode = ""
        unit = ""
        alert_data = await state.get_data()
        await state.update_data(time=str(result))
        if alert_data['mode'] == "reaching":
            mode = "Достижение цены"
            unit = sm.wallet(alert_data['ticker'])
        elif alert_data['mode'] == "increased_vol":
            mode = "Повышенный дневной объём (%)"
            unit = "%"
        elif alert_data['mode'] == "day_increase":
            mode = "Внутридневное движение цены вверх"
            unit = sm.wallet(alert_data['ticker'])
        elif alert_data['mode'] == "day_decrease":
            mode = "Внутридневное движение цены вниз"
            unit = sm.wallet(alert_data['ticker'])
        elif alert_data['mode'] == "day_increase_percent":
            mode = "Внутридневное движение цены вверх (%)"
            unit = "%"
        elif alert_data['mode'] == "day_decrease_percent":
            mode = "Внутридневное движение цены вниз (%)"
            unit = "%"
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text="<b>Добавление алерта: </b>\n\n<b>Тикер: </b>" + alert_data['ticker'] +
                                         "\n<b>Режим: </b>" + mode + "\n<b>Значение: </b>" + alert_data['value'] + " " +
                                         unit + "\n<b>Сообщение: </b>" +
                                         alert_data['message'] + "\n<b>Тип алерта: </b>срочный\n<b>"
                                                                 "Дата окончания действия алерта: </b>" +
                                         str(result.day) + "." + str(result.month) + "." + str(result.year),
                                    parse_mode="HTML", reply_markup=kb.alert_accept_menu)
        await AddAlert.next()


# выбор бессрочного или срочного режима
@dp.callback_query_handler(lambda call: True, state=AddAlert.time)
async def alert_get_date(call, state: FSMContext):
    if call.data == "definite":
        calendar, step = DetailedTelegramCalendar(locale='ru').build()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f"Выберите год", reply_markup=calendar)
    if call.data == "indefinite":
        mode = ""
        unit = ""
        await state.update_data(time="4000-01-01")
        alert_data = await state.get_data()

        if alert_data['mode'] == "reaching":
            mode = "Достижение цены"
            unit = sm.wallet(alert_data['ticker'])
        elif alert_data['mode'] == "increased_vol":
            mode = "Повышенный дневной объём (%)"
            unit = "%"
        elif alert_data['mode'] == "day_increase":
            mode = "Внутридневное движение цены вверх"
            unit = sm.wallet(alert_data['ticker'])
        elif alert_data['mode'] == "day_decrease":
            mode = "Внутридневное движение цены вниз"
            unit = sm.wallet(alert_data['ticker'])
        elif alert_data['mode'] == "day_increase_percent":
            mode = "Внутридневное движение цены вверх (%)"
            unit = "%"
        elif alert_data['mode'] == "day_decrease_percent":
            mode = "Внутридневное движение цены вниз (%)"
            unit = "%"
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="<u><b>Добавление алерта:</b></u>"
                                         "\n\n<b>Тикер: </b>" +
                                         alert_data['ticker'] + "\n<b>Режим: </b>" + mode + "\n<b>Значение: </b>" +
                                         alert_data['value'] + " " + unit + "\n<b>Сообщение:</b> "
                                         + alert_data['message'] + "\n<b>Тип алерта:</b> бессрочный", parse_mode="HTML",
                                    reply_markup=kb.alert_accept_menu)
        await AddAlert.next()


# отмена или добавление алерта в БД
@dp.callback_query_handler(lambda call: True, state=AddAlert.accept)
async def accept_alert(call, state: FSMContext):
    if call.data == "accept":
        alert_data = await state.get_data()
        db.add_alert(call.message.chat.id, alert_data['ticker'], alert_data['mode'],
                     alert_data['value'], alert_data['message'], alert_data['time'], date.normal_now())
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Алерт добавлен", reply_markup=kb.standart_kb)
        await bot.send_message(call.message.chat.id, text=messages.alerts, parse_mode="HTML",
                                    reply_markup=kb.univAlMenu)
        await state.finish()
    if call.data == "cancel":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Добавление алерта отменено")
        await bot.send_message(call.message.chat.id, messages.alert_full_info(call.message.chat.id, active_id),
                               reply_markup=kb.edit_active_alert_menu, parse_mode='HTML')
        await state.finish()
    if call.data == "edit_alert":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Введите тикер")
        await AddAlert.first()


# ------------------------------------КОМАНДЫ, ОТВЕЧАЮЩИЕ ЗА РЕДАКТИРОВАНИЕ-------------------------------


# команды, отвечающие за редактирование алертов
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def alerts_editor(message: types.message):
    global active_id
    if re.sub(r'[^\w\s]+|[\d]+', r'', message.text).strip() == "_note":
        await bot.send_message(message.from_user.id, messages.alert_full_info(message.from_user.id,
                                                                              re.sub("\D", "", message.text)),
                               reply_markup=kb.edit_active_alert_menu, parse_mode='HTML')
        active_id = re.sub("\D", "", message.text)
    elif re.sub(r'[^\w\s]+|[\d]+', r'', message.text).strip() == "_log":
        await bot.send_message(message.from_user.id, messages.alert_full_info(message.from_user.id,
                                                                              re.sub("\D", "", message.text)),
                               reply_markup=kb.edit_executed_alert_menu, parse_mode='HTML')
        active_id = re.sub("\D", "", message.text)
    elif re.sub(r'[^\w\s]+|[\d]+', r'', message.text).strip() == "_portfolio":
        await bot.send_message(message.from_user.id, messages.portfolio_full_info(message.from_user.id,
                                                                                  re.sub("\D", "", message.text)),
                               reply_markup=kb.edit_portfolio_menu, parse_mode='HTML')
        active_id = re.sub("\D", "", message.text)


# --------------------------------------------РЕДАКТИРОВАНИЕ ПОРТФЕЛЯ-------------------------------------


# подтверждение удаления портфеля
@dp.callback_query_handler(lambda call: True, state=EditPortfolio.delete_portfolio)
async def delete_portfolio(call, state: FSMContext):
    if call.data == "accept":
        db.delete_portfolio(call.message.chat.id, active_id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.my_portfolios(call.message.chat.id), parse_mode='HTML',
                                    reply_markup=kb.my_portfolios_menu)
        await state.finish()
    if call.data == "cancel":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.portfolio_full_info(call.message.chat.id, active_id),
                                    reply_markup=kb.edit_portfolio_menu, parse_mode='HTML')
        await state.finish()


# --------------------------------------------РЕДАКТИРОВАНИЕ АЛЕРТА---------------------------------------


# редактирование тикера
@dp.message_handler(state=EditAlert.edit_ticker, content_types=types.ContentTypes.TEXT)
async def alert_edit_ticker(message: types.Message, state: FSMContext):
    global active_id
    if not sm.ticker_exists(message.text.upper()):
        await bot.send_message(message.from_user.id, messages.ticker_not_exists)
        return
    db.alert_change_ticker(message.text.upper(), message.from_user.id, active_id)
    db.add_alert_edit_date(message.from_user.id, active_id)
    await bot.send_message(message.from_user.id, messages.alert_full_info(message.from_user.id, active_id),
                           reply_markup=kb.edit_active_alert_menu, parse_mode='HTML')

    await state.finish()


# редактирование режима алерта
@dp.callback_query_handler(lambda call: True, state=EditAlert.edit_mode)
async def alert_edit_mode(call, state: FSMContext):
    global active_id
    if call.data == "reaching":
        await state.update_data(edit_mode=call.data)
        await EditAlert.next()
        await bot.send_message(call.message.chat.id,
                               messages.mode_message(db.alert_info_by_individual_id(call.message.chat.id,
                                                                                    active_id)[0][2]))
    if call.data == "increased_vol":
        await state.update_data(edit_mode=call.data)
        await EditAlert.next()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Введите процент увеличения объёма от нормы:")
    if call.data == "day_increase":
        await state.update_data(edit_mode=call.data)
        await EditAlert.next()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Введите значение увеличения цены внутри дня:")
    if call.data == "day_decrease":
        await state.update_data(edit_mode=call.data)
        await EditAlert.next()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Введите значение уменьшения цены внутри дня:")
    if call.data == "day_increase_percent":
        await state.update_data(edit_mode=call.data)
        await EditAlert.next()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Введите процент увеличения цены внутри дня:")
    if call.data == "day_decrease_percent":
        await state.update_data(edit_mode=call.data)
        await EditAlert.next()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Введите процент уменьшения цены внутри дня:")


# редактирование значения алерта
@dp.message_handler(state=EditAlert.edit_value, content_types=types.ContentTypes.TEXT)
async def alert_edit_value(message: types.Message, state: FSMContext):
    global active_id
    mode = ""
    if not sm.is_value(message.text) or (sm.is_value(message.text) and (int(message.text) < 0)):
        await bot.send_message(message.from_user.id, "Введите корректное значение")
        return
    await state.update_data(edit_value=sm.make_value(message.text))
    edited_alert_data = await state.get_data()
    if edited_alert_data['edit_mode'] == "reaching" and float(sm.price(db.alert_info_by_individual_id(
            message.from_user.id, active_id)[0][2])) <= float(edited_alert_data['edit_value']):
        mode = ">="
    if edited_alert_data['edit_mode'] == "reaching" and float(sm.price(db.alert_info_by_individual_id(
            message.from_user.id, active_id)[0][2])) > float(edited_alert_data['edit_value']):
        mode = "<="
    if edited_alert_data['edit_mode'] == "increased_vol":
        mode = "increased_vol"
    else:
        mode = edited_alert_data['edit_mode']
    db.alert_change_mode_and_value(mode, edited_alert_data['edit_value'],
                                   message.from_user.id, active_id)
    db.add_alert_edit_date(message.from_user.id, active_id)
    await bot.send_message(message.from_user.id, messages.alert_full_info(message.from_user.id, active_id),
                           reply_markup=kb.edit_active_alert_menu, parse_mode='HTML')
    await state.finish()


# редактирование сообщения-ответа
@dp.message_handler(state=EditAlert.edit_message, content_types=types.ContentTypes.TEXT)
async def alert_edit_message(message: types.Message, state: FSMContext):
    global active_id
    db.alert_change_message(message.text, message.from_user.id, active_id)
    db.add_alert_edit_date(message.from_user.id, active_id)
    await bot.send_message(message.from_user.id, messages.alert_full_info(message.from_user.id, active_id),
                           reply_markup=kb.edit_active_alert_menu, parse_mode='HTML')
    await state.finish()


# инлайновый календарь для редактирования
@dp.callback_query_handler(DetailedTelegramCalendar.func(), state=EditAlert.edit_time)
async def edit_inline_kb_answer_callback_handler(call, state: FSMContext):
    result, key, step = DetailedTelegramCalendar(current_date=datetime.datetime.now().today().date(),
                                                 min_date=datetime.datetime.now().today().date(),
                                                 locale='ru').process(call.data)
    a = ""
    if not result and key:
        if LSTEP[step] == "month":
            a = "месяц"
        elif LSTEP[step] == "day":
            a = "день"
        await bot.edit_message_text(f"Выберите {a}",
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=key)
    elif result:
        db.alert_change_time(str(result), call.message.chat.id, active_id)
        db.add_alert_edit_date(call.message.chat.id, active_id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.alert_full_info(call.message.chat.id, active_id),
                                    reply_markup=kb.edit_active_alert_menu, parse_mode='HTML')
        await state.finish()


# редактирование времени действия
@dp.callback_query_handler(lambda call: True, state=EditAlert.edit_time)
async def alert_edit_date(call, state: FSMContext):
    global active_id
    if call.data == "definite":
        calendar, step = DetailedTelegramCalendar(locale='ru').build()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f"Выберите год", reply_markup=calendar)
    if call.data == "indefinite":
        db.alert_change_time("4000-01-01", call.message.chat.id, active_id)
        db.add_alert_edit_date(call.message.chat.id, active_id)
        await bot.send_message(call.message.chat.id, messages.alert_full_info(call.message.chat.id, active_id),
                               reply_markup=kb.edit_active_alert_menu, parse_mode='HTML')
        await state.finish()


# подтверждение удаления алерта
@dp.callback_query_handler(lambda call: True, state=EditAlert.delete_alert)
async def delete_alert(call, state: FSMContext):
    if call.data == "accept":
        db.delete_alert(call.message.chat.id, active_id)
        kb.active_alerts = InlineKeyboardButton('Активные алерты [' +
                                                str(len(db.active_alerts_list(call.message.chat.id))) +
                                                ']', callback_data='active_alerts')
        kb.executed_alerts = InlineKeyboardButton('Выполненные алерты [' +
                                                  str(len(db.executed_alerts_list(call.message.chat.id))) +
                                                  ']', callback_data='executed_alerts')
        kb.alMenu = InlineKeyboardMarkup(row_width=1).add(kb.active_alerts, kb.executed_alerts
                                                          , kb.add_alert,
                                                          kb.backToMainMenu)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.alerts, reply_markup=kb.alMenu)
        await state.finish()
    if call.data == "cancel":
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.alert_full_info(call.message.chat.id, active_id),
                                    reply_markup=kb.edit_active_alert_menu, parse_mode='HTML')
        await state.finish()


# ------------------------------------------МЕНЮ "НАСТРОЙКИ"----------------------------------------------


# функция для изменения меню настроек в зависимости от выбранных параметров пользователя
async def change_settings_keyboard(user_id):
    if db.is_on_email_alert(user_id):
        kb.mail_alert = InlineKeyboardButton("🔔 Дублировать алерт на электронную почту: ВКЛ",
                                             callback_data='mail_alert')
    else:
        kb.mail_alert = InlineKeyboardButton("🔕 Дублировать алерт на электронную почту: ВЫКЛ",
                                             callback_data='mail_alert')
    if db.mail_exists(user_id):
        kb.add_mail = InlineKeyboardButton("✏️Изменить адрес электронной почты", callback_data='add_mail')
    else:
        kb.add_mail = InlineKeyboardButton("🖨Добавить адрес электронной почты", callback_data='add_mail')
    kb.settings_menu = InlineKeyboardMarkup(row_width=1).add(kb.mail_alert, kb.add_mail, kb.backToMainMenu)


# обработчик кнопки "назад" при добавлении электронной почты
@dp.callback_query_handler(lambda call: True, state="*")
async def back_to_main_menu(call, state: FSMContext):
    if call.data == "backToSettingsMenu":
        await change_settings_keyboard(call.message.chat.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=messages.settings_menu(call.message.chat.id),
                                    reply_markup=kb.settings_menu, parse_mode="HTML")
        await state.finish()


# обработчик кнопки "добавить" или "изменить" адрес электронной почты
@dp.message_handler(state=EmailChange.email, content_types=types.ContentTypes.TEXT)
async def alert_get_mail(message: types.Message, state: FSMContext):
    if not mail.is_email(message.text):
        await bot.send_message(message.from_user.id, messages.not_mail)
        return
    global code
    code = str(random.randint(100000, 999999))
    mail.send_message(message.text, messages.check_email(code), "Проверка почты @mhfi_bot")
    await bot.send_message(message.from_user.id, "<b>Введите код подтверждения, отправленный вам на почту:</b>\n\n"
                                                 "Если письма нет в папке \"входящие\", проверьте папку \"Спам\"",
                           parse_mode='HTML', reply_markup=kb.toSettings)
    await state.update_data(email=message.text)
    await EmailChange.next()


# проверка принадлежности почты пользователю
@dp.message_handler(state=EmailChange.check, content_types=types.ContentTypes.TEXT)
async def alert_check_mail(message: types.Message, state: FSMContext):
    global code
    global i
    if code == message.text:
        email = await state.get_data()
        if not db.mail_exists(message.from_user.id):
            db.add_mail(message.from_user.id, email['email'])
            await bot.send_message(message.from_user.id, "Электронная почта добавлена")
        else:
            db.change_mail(message.from_user.id, email['email'])
            await bot.send_message(message.from_user.id, "Электронная почта изменена")
        db.alert_mail_on(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, "Код неверный. Попробуйте еще раз."
                                                     "\nОсталось попыток: " + str(4 - i))
        i = i + 1
        if i == 5:
            i = 0
            await bot.send_message(message.from_user.id, "Введите почту повторно: ")
            await EmailChange.email.set()
        return
    await change_settings_keyboard(message.from_user.id)
    await bot.send_message(chat_id=message.from_user.id, text=messages.settings_menu(message.from_user.id),
                           reply_markup=kb.settings_menu, parse_mode="HTML")
    await state.finish()


# ------------------------------------ФУНКЦИИ ДЛЯ СРАБАТЫВАНИЯ АЛЕРТОВ------------------------------------


# функция алертов, отвечающая за достижение цены
async def alert_main(delay):
    while True:
        await asyncio.sleep(delay)
        tickers = db.get_unique_tickers()
        for selectedTicker in tickers:
            local_price = sm.price(selectedTicker)
            ticker_notes = db.find_active_alerts_by_ticker(selectedTicker)
            for selectedNote in ticker_notes:
                if selectedNote[6]:
                    if selectedNote[4] == ">=" and float(local_price) >= float(selectedNote[3]):
                        await bot.send_message(selectedNote[1], messages.alert_message(selectedTicker,
                                                                                       selectedNote[4],
                                                                                       selectedNote[3],
                                                                                       selectedNote[5]),
                                               parse_mode='HTML', reply_markup=kb.standart_kb)
                        if db.is_on_email_alert(selectedNote[1]):
                            mail.send_message(db.get_email(selectedNote[1]),
                                              messages.mail_alert_message(selectedTicker, selectedNote[4],
                                                                          selectedNote[3], selectedNote[5]))
                        db.alert_off(selectedNote[1], selectedNote[7])
                    if selectedNote[4] == "<=" and float(local_price) <= float(selectedNote[3]):
                        await bot.send_message(chat_id=selectedNote[1], text=messages.alert_message(selectedTicker,
                                                                                                    selectedNote[4],
                                                                                                    selectedNote[3],
                                                                                                    selectedNote[5]),
                                               parse_mode='Markdown', reply_markup=kb.standart_kb)
                        if db.is_on_email_alert(selectedNote[1]):
                            mail.send_message(db.get_email(selectedNote[1]),
                                              messages.mail_alert_message(selectedTicker, selectedNote[4],
                                                                          selectedNote[3], selectedNote[5]))
                        db.alert_off(selectedNote[1], selectedNote[7])


# функция алертов, отвечающая за объёмы
async def alert_vol(delay):
    while True:
        await asyncio.sleep(delay)
        tickers = db.get_unique_tickers()
        for selectedTicker in tickers:
            ticker_notes = db.find_active_alerts_by_ticker(selectedTicker)
            for selectedNote in ticker_notes:
                if selectedNote[4] == "increased_vol" and sm.finviz_volume_compare(selectedTicker) > \
                        (selectedNote[3] / 100 + 1):
                    await bot.send_message(chat_id=selectedNote[1], text=messages.volume_alert_message(selectedTicker,
                                                                                                       selectedNote[5]),
                                           parse_mode='HTML', reply_markup=kb.standart_kb)
                    if db.is_on_email_alert(selectedNote[1]):
                        mail.send_message(db.get_email(selectedNote[1]),
                                          messages.mail_volume_alert_message(selectedTicker, selectedNote[5]))
                    db.alert_off(selectedNote[1], selectedNote[7])
            sm.finviz_clear_cache()


# функция алертов, исполняющаяся раз в день, отвечающая за отключение просроченных алертов
async def off_overdue_alerts():
    while True:
        await asyncio.sleep(86400)
        active_alerts = db.get_active_alerts()
        for selectedNote in active_alerts:
            if datetime.datetime.strptime(selectedNote[8], "%Y-%m-%d").date() < datetime.datetime.now().date():
                db.alert_off(selectedNote[1], selectedNote[7])


# функция алертов, отвечающая за внутридневное движение цены
async def increase_decrease_alerts(delay):
    while True:
        await asyncio.sleep(delay)
        tickers = db.get_unique_tickers()
        for selectedTicker in tickers:
            ticker_notes = db.find_active_alerts_by_ticker(selectedTicker)
            for selectedNote in ticker_notes:
                if selectedNote[4] == "day_increase" and sm.day_price_change(selectedTicker) >= selectedNote[3]:
                    await bot.send_message(selectedNote[1],
                                           messages.increase_alert_message(selectedTicker, selectedNote[5]),
                                           parse_mode='HTML', reply_markup=kb.standart_kb)
                    if db.is_on_email_alert(selectedNote[1]):
                        mail.send_message(db.get_email(selectedNote[1]),
                                          messages.mail_increase_alert_message(selectedTicker, selectedNote[5]))
                    db.alert_off(selectedNote[1], selectedNote[7])
                if selectedNote[4] == "day_decrease" and sm.day_price_change(selectedTicker) <= -selectedNote[3]:
                    await bot.send_message(selectedNote[1],
                                           messages.decrease_alert_message(selectedTicker, selectedNote[5]),
                                           parse_mode='HTML', reply_markup=kb.standart_kb)
                    if db.is_on_email_alert(selectedNote[1]):
                        mail.send_message(db.get_email(selectedNote[1]),
                                          messages.mail_decrease_alert_message(selectedTicker, selectedNote[5]))
                    db.alert_off(selectedNote[1], selectedNote[7])
                if selectedNote[4] == "day_increase_percent" and sm.day_price_change_percent(selectedTicker) >= \
                        selectedNote[3]:
                    await bot.send_message(selectedNote[1],
                                           messages.increase_alert_message_percent(selectedTicker, selectedNote[5]),
                                           parse_mode='HTML', reply_markup=kb.standart_kb)
                    if db.is_on_email_alert(selectedNote[1]):
                        mail.send_message(db.get_email(selectedNote[1]),
                                          messages.mail_increase_alert_message_percent(selectedTicker, selectedNote[5]))
                    db.alert_off(selectedNote[1], selectedNote[7])
                if selectedNote[4] == "day_decrease_percent" and sm.day_price_change_percent(selectedTicker) <= - \
                        selectedNote[3]:
                    await bot.send_message(selectedNote[1],
                                           messages.decrease_alert_message_percent(selectedTicker, selectedNote[5]),
                                           parse_mode='HTML', reply_markup=kb.standart_kb)
                    if db.is_on_email_alert(selectedNote[1]):
                        mail.send_message(db.get_email(selectedNote[1]),
                                          messages.mail_decrease_alert_message_percent(selectedTicker, selectedNote[5]))
                    db.alert_off(selectedNote[1], selectedNote[7])


# ---------------------------------------------ЛОНГ ПОЛЛИНГ-----------------------------------------------

# запуск лонг поллинга
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(alert_main(15))
    loop.create_task(alert_vol(15))
    loop.create_task(off_overdue_alerts())
    loop.create_task(increase_decrease_alerts(15))
    executor.start_polling(dp, skip_updates=True)
