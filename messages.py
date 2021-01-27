import sm_info as sm
from db_manipulator import Database
import date
import json
import requests
import tickers
db = Database('users.db')

main_menu = "ГЛАВНОЕ МЕНЮ"
not_mail = "Введите корректный адрес электронной почты"
email_enter = "Введите адрес электронной почты, на который вы хотите получать алерты"
about_us = "Здесь будет размещена информация о нас"
my_stocks = """Здесь будет текст калькулятора"""
alerts = """
Здесь будет размещена информация об алертах
"""
add_alert_first_step = "Введите тикер:\n\n*Если тикер принадлежит европейской бирже, " \
                       "введите её название через точку (Например, ADS.DE)"
ticker_not_exists = "Введите существующий тикер"
feedback = "Здесь вы можете оставить свои мысли, как можно дополнить бот, указать на ошибки, возникшие в ходе " \
           "использования бота или написать любую другую информацию, которую вы желаете передать " \
           "администрации mhfi_bot."
description = """<b>Многофункциональный помощник для инвестирования. 🤖</b>

<b>Функции бота:</b>

<b>1️⃣ Калькулятор ценных бумаг.</b>
      🔸Подсчёт доходности.
      🔸Диаграмма по отраслям.
      🔸Диаграмма по валютам.
      🔸Диаграмма по количеству каждой бумаги в портфеле.
<b>2️⃣ Оповещения на цену.</b>
      🔸Все акции рынка США.
      🔸Все️ акции Московской биржи.
      🔸Все акции Санкт-Петербургской биржи.
   
<b>Количество создаваемых оповещений неограниченно.</b>

<b>Сервис бесплатный.</b>

@mhfi_bot"""


def alert_full_info(owner, individual_alert_id):
    info = db.alert_info_by_individual_id(owner, individual_alert_id)
    mode = ""
    message = ""
    unit = ""
    edit_date = ""
    if info[0][11] == "4000-01-01":
        edit_date = "\n<b>Алерт не редактировался</b>"
    else:
        edit_date = "<b>\nПоследнее редактирование: </b>" + info[0][11]
    if info[0][4] == "increased_vol":
        mode = "Объём за день возрос от нормы на %"
        unit = "%"
    elif info[0][4] == ">=" or info[0][4] == "<=":
        mode = "Достижение цены"
        unit = sm.wallet(info[0][2])
    elif info[0][4] == "day_increase":
        mode = "Внутридневное движение цены вверх"
        unit = sm.wallet(info[0][2])
    elif info[0][4] == "day_decrease":
        mode = "Внутридневное движение цены вниз"
        unit = sm.wallet(info[0][2])
    elif info[0][4] == "day_increase_percent":
        mode = "Внутридневное движение цены вверх (%)"
        unit = "%"
    elif info[0][4] == "day_decrease_percent":
        mode = "Внутридневное движение цены вниз (%)"
        unit = "%"
    if info[0][8] == "4000-01-01":
        message = "<b>Тикер: </b>" + \
                  str(info[0][2]) + "\n<b>Значение: </b>" + \
                  str(info[0][3]) + " " + unit \
                  + "\n<b>Режим алерта: </b>" + mode + "\n<b>Тип алерта: </b>Бессрочный" + "\n<b>Сообщение: </b>" + \
                  str(info[0][5]) + "\n\n--------------------\n<b>Добавление: </b>" + \
                  info[0][10] + edit_date

    else:
        message = "<b>Тикер: </b>" + \
                  str(info[0][2]) + "\n<b>Значение: </b>" + \
                  str(info[0][3]) + " " + unit \
                  + "\n<b>Режим алерта: </b>" + mode + "\n<b>Тип алерта: </b>Срочный\n" + "<b>Срок действия: </b>" + \
                  date.normalize_date(info[0][8]) + "\n<b>Сообщение: </b>" + str(info[0][5]) + \
                  "\n\n--------------------\n<b>Добавлен: </b>" + \
                  info[0][10] + edit_date
    if str(info[0][6]) == "0":
        message = message + "\n<b>Отключен/выполнен: </b>" + info[0][9]
    return message


def deactive_alerts(user_id):
    mode = ""
    unit = ""
    message = "<u><b>Выполненные алерты:</b></u>\n\n/"
    info = db.executed_alerts_list(user_id)
    for n in range(len(info)):
        if info[n][4] == "increased_vol":
            mode = "Объём за день возрос от нормы на %"
            unit = "%"
        elif info[n][4] == ">=" or info[n][4] == "<=":
            mode = "Достижение цены"
            unit = sm.wallet(info[n][2])
        elif info[n][4] == "day_increase":
            mode = "Внутридневное движение цены вверх"
            unit = sm.wallet(info[n][2])
        elif info[n][4] == "day_decrease":
            mode = "Внутридневное движение цены вниз"
            unit = sm.wallet(info[n][2])
        elif info[n][4] == "day_increase_percent":
            mode = "Внутридневное движение цены вверх (%)"
            unit = "%"
        elif info[n][4] == "day_decrease_percent":
            mode = "Внутридневное движение цены вниз (%)"
            unit = "%"
        if info[n][8] == "4000-01-01":
            message = message + str(info[n][7]) + "_log\n<b>Тикер: </b>" + \
                      str(info[n][2]) + "\n<b>Значение: </b>" + \
                      str(info[n][3]) + " " + unit \
                      + "\n<b>Режим алерта: </b>" + mode + "\n<b>Тип алерта: </b>Бессрочный" + "\n<b>Сообщение: </b>" + \
                      str(info[n][5]) + "\n\n/"

        else:
            message = message + str(info[n][7]) + "_log\n<b>Тикер: </b>" + \
                      str(info[n][2]) + "\n<b>Значение: </b>" + \
                      str(info[n][3]) + " " + unit \
                      + "\n<b>Режим алерта: </b>" + mode + "\n<b>Тип алерта: </b>Срочный\n" + "<b>Срок действия: </b>" + \
                      date.normalize_date(info[n][8]) + "\n<b>Сообщение: </b>" + \
                      str(info[n][5]) + "\n\n/"

    return message[0:-1] + "--------------------\nДля редактирования алерта нажмите на его номер"


def active_alerts(user_id):
    unit = ""
    mode = ""
    message = "<u><b>Активные алерты:</b></u>\n\n/"
    info = db.active_alerts_list(user_id)
    for n in range(len(info)):
        if info[n][4] == "increased_vol":
            mode = "Объём за день возрос от нормы на %"
            unit = "%"
        elif info[n][4] == ">=" or info[n][4] == "<=":
            mode = "Достижение цены"
            unit = sm.wallet(info[n][2])
        elif info[n][4] == "day_increase":
            mode = "Внутридневное движение цены вверх"
            unit = sm.wallet(info[n][2])
        elif info[n][4] == "day_decrease":
            mode = "Внутридневное движение цены вниз"
            unit = sm.wallet(info[n][2])
        elif info[n][4] == "day_increase_percent":
            mode = "Внутридневное движение цены вверх (%)"
            unit = "%"
        elif info[n][4] == "day_decrease_percent":
            mode = "Внутридневное движение цены вниз (%)"
            unit = "%"
        if info[n][8] == "4000-01-01":
            message = message + str(info[n][7]) + "_note\n<b>Тикер: </b>" + \
                      str(info[n][2]) + "\n<b>Значение: </b>" + \
                      str(info[n][3]) + " " + unit \
                      + "\n<b>Режим алерта: </b>" + mode + "\n<b>Тип алерта: </b>Бессрочный" + "\n<b>Сообщение: </b>" + \
                      str(info[n][5]) + "\n\n/"

        else:
            message = message + str(info[n][7]) + "_note\n<b>Тикер: </b>" + \
                      str(info[n][2]) + "\n<b>Значение: </b>" + \
                      str(info[n][3]) + " " + unit \
                      + "\n<b>Режим алерта: </b>" + mode + "\n<b>Тип алерта: </b>Срочный\n" + "<b>Срок действия: </b>" + \
                      date.normalize_date(info[n][8]) + "\n<b>Сообщение: </b>" + \
                      str(info[n][5]) + "\n\n/"

    return message[0:-1] + "--------------------\nДля редактирования алерта нажмите на его номер"


def mode_message(ticker):
    return "Цена сейчас: " + sm.price_spr(ticker) + "\nВведите значение (валюту вводить не нужно): "


def alert_message(ticker, mode, price, message):
    return "*#Алерт*\n" + ticker + mode + str(price) + "\n*Текущее значение: *" + str(sm.price_spr(ticker)) \
           + "\n*Сообщение: *" + str(message)


def mail_alert_message(ticker, mode, price, message):
    return ticker + mode + str(price) + "\nТекущее значение: " + str(sm.price_spr(ticker)) + "\nСообщение: " + \
           str(message) + "\n\n\nС уважением, @mhfi_bot"


def volume_alert_message(ticker, message):
    return "<b>#Алерт</b>\nДневной объём " + ticker + " повышен на " + \
           str(round(((sm.finviz_volume_compare(ticker) - 1) * 100), 1)) + "%\n<b>Сообщение: </b>" + str(message)


def mail_volume_alert_message(ticker, message):
    return "Дневной объём " + ticker + " повышен на " + \
           str(round(((sm.finviz_volume_compare(ticker) - 1) * 100), 1)) + "%\nСообщение: " + str(message) + \
           "\n\n\nС уважением, @mhfi_bot"


def increase_alert_message(ticker, message):
    return "<b>#Алерт</b>\nЦена " + ticker + " за день была повышена на " + \
           str(sm.day_price_change(ticker)) + " " + sm.wallet(ticker) + "\n<b>Сообщение: </b>" + str(message)


def mail_increase_alert_message(ticker, message):
    return "Цена " + ticker + " за день была повышена на " + \
           str(sm.day_price_change(ticker)) + " " + sm.wallet(ticker) + "\nСообщение: " + str(message) + \
           "\n\n\nС уважением, @mhfi_bot"


def decrease_alert_message(ticker, message):
    return "<b>#Алерт</b>\nЦена " + ticker + " за день была понижена на " + \
           str(sm.day_price_change(ticker)) + " " + sm.wallet(ticker) + "\n<b>Сообщение: </b>" + str(message)


def mail_decrease_alert_message(ticker, message):
    return "Цена " + ticker + " за день была понижена на " + \
           str(sm.day_price_change(ticker)) + " " + sm.wallet(ticker) + "\nСообщение: " + str(message) + \
           "\n\n\nС уважением, @mhfi_bot"


def increase_alert_message_percent(ticker, message):
    return "<b>#Алерт</b>\nЦена " + ticker + " за день была повышена на " + \
           str(sm.day_price_change(ticker)) + " " + "%\n<b>Сообщение: </b>" + str(message)


def mail_increase_alert_message_percent(ticker, message):
    return "Цена " + ticker + " за день была повышена на " + \
           str(sm.day_price_change(ticker)) + " " + "%\nСообщение: " + str(message) + \
           "\n\n\nС уважением, @mhfi_bot"


def decrease_alert_message_percent(ticker, message):
    return "<b>#Алерт</b>\nЦена " + ticker + " за день была понижена на " + \
           str(sm.day_price_change(ticker)) + " " + "%\n<b>Сообщение: </b>" + str(message)


def mail_decrease_alert_message_percent(ticker, message):
    return f"Цена {ticker} за день была понижена на {str(sm.day_price_change(ticker))} " \
           f"%\nСообщение: {str(message)}\n\n\nС уважением, @mhfi_bot"


def settings_menu(user_id):
    try:
        return f"<b>НАСТРОЙКИ</b>\n\n<b>Добавленный адрес электронной почты:</b>\n{db.get_email(user_id)}" \
               f"\n\n*На кнопках отображается текущее значение параметра"
    except:
        return "<b>НАСТРОЙКИ</b>\n\nАдрес электронной почты не добавлен\n\n\*На к" \
               "нопках отображается текущее значение параметра"


def check_email(code):
    return f"Код подтверждения почтового адреса: {code}\n\nЕсли код был запрошен не вами, " \
           f"проигнорируйте это сообщение\n\n\nС уважением, @mhfi_bot"


def ticker_info(ticker):
    message = "<b>Информация о компании</b> "
    if ticker in tickers.moex_tickers:
        yahoo_first_link = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}.ME?modules=price").content
        yahoo_second_link = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}.ME?modules=assetProfile").content
        wallet = "RUB"
        price = str(sm.get_moex_price(ticker)) + " " + wallet

    else:
        yahoo_first_link = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=price").content
        yahoo_second_link = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=assetProfile").content
        wallet = json.loads(yahoo_first_link)["quoteSummary"]["result"][0]["price"]["currency"]
        price = str(json.loads(yahoo_first_link)["quoteSummary"]["result"][0]["price"]["regularMarketPrice"]["raw"]) + " " + wallet

    day_price_change = str(
        json.loads(yahoo_first_link)["quoteSummary"]["result"][0]['price']['regularMarketChange']['fmt'])
    day_price_change_percent = str(
        json.loads(yahoo_first_link)["quoteSummary"]["result"][0]['price']['regularMarketChangePercent']['fmt'])
    exchange = json.loads(yahoo_first_link)["quoteSummary"]["result"][0]["price"]["exchange"]
    sector = json.loads(yahoo_second_link)["quoteSummary"]["result"][0]["assetProfile"]["sector"]
    industry = json.loads(yahoo_second_link)["quoteSummary"]["result"][0]["assetProfile"]["industry"]

    message += json.loads(yahoo_first_link)["quoteSummary"]["result"][0]["price"]["longName"]

    message += f"\n------------------------------------------------------\n<b>Цена:</b> {price}\n" \
               f"<b>Изменение цены за день:</b> {day_price_change} {wallet} ({day_price_change_percent}%)\n" \
               f"{sm.ytd_return(ticker)}{sm.dividend(ticker)}\n<b>Биржа:</b> {exchange}\n" \
               f"<b>Направление:</b> {industry}\n<b>Отрасль:</b> {sector}"

    if not "." in ticker and ticker not in tickers.moex_tickers:
        message += f"\n<b>Zacks rank:</b> {sm.zacks_rank(ticker)}"
    return message
