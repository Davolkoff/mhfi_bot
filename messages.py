import sm_info as sm
from db_manipulator import Database
import date
import json
import requests
import tickers
import datetime
db = Database('users.db')

main_menu = "ГЛАВНОЕ МЕНЮ"
not_mail = "Введите корректный адрес электронной почты"
email_enter = "Введите адрес электронной почты, на который вы хотите получать алерты"
about_us = """Бот создан независимыми разработчиками группы 8В02 в рамках творческого проекта в Томском Политехническом университете👨‍🎓

    ⚡️<b>Разработчики:</b>⚡️

    👨‍⚖️Волков Даниил Алексеевич
    🥷Архипов Данил Александрович

    @mhfi_bot
    """

header = { 
'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36', 
'upgrade-insecure-requests': '1', 
'cookie': 'mos_id=CllGxlx+PS20pAxcIuDnAgA=; session-cookie=158b36ec3ea4f5484054ad1fd21407333c874ef0fa4f0c8e34387efd5464a1e9500e2277b0367d71a273e5b46fa0869a; NSC_WBS-QUBG-jo-nptsv-WT-443=ffffffff0951e23245525d5f4f58455e445a4a423660; rheftjdd=rheftjddVal; _ym_uid=1552395093355938562; _ym_d=1552395093; _ym_isad=2' 
}

alerts = """
🚨<b>Алерты</b>🚨
Типы оповещений:
▫️Оповещения на достижение ценой заданного значения
▫️Оповещения на повышенный дневной объём
▫️Оповещения на внутреднемное движение цены

<b>Подключенные биржи:</b>

🇺🇸New York Stock Exchange (NYSE)
🇺🇸NASDAQ
🇺🇸NYSE Arca (PSE)
🇺🇸Cboe BZX US Equities Exchange
🇺🇸NYSE American (ASE)
🇷🇺Московская биржа

"""
add_alert_first_step = "Введите тикер:\n\n*Если тикер принадлежит европейской бирже, " \
                       "введите её название через точку (Например, ADS.DE)"
ticker_not_exists = "Введите существующий тикер"
feedback = "Здесь вы можете оставить свои мысли, как можно дополнить бот, указать на ошибки, возникшие в ходе " \
           "использования бота или написать любую другую информацию, которую вы желаете передать " \
           "администрации mhfi_bot."
description = """<b>Многофункциональный помощник для инвестирования. 🤖</b>

<b>Функции бота:</b>

<b>1️⃣ Калькулятор ценных бумаг:</b>
      🔸Подсчёт доходности.
      🔸Диаграмма по отраслям.
      🔸Диаграмма по валютам.
      🔸Диаграмма по количеству каждой бумаги в портфеле.
<b>2️⃣ Оповещения на цену (алерты):</b>
      🔸Отправка оповещений на электронную почту
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
        message = "🏷<b>Тикер: </b>" + \
                  str(info[0][2]) + "\n🎚<b>Значение: </b>" + \
                  str(info[0][3]) + " " + unit \
                  + "\n📇<b>Режим алерта: </b>" + mode + "\n⏰<b>Тип алерта: </b>Бессрочный" + "\n✉️<b>Сообщение: </b>" + \
                  str(info[0][5]) + "\n\n-----------------------------------------------\n<b>Добавление: </b>" + \
                  info[0][10] + edit_date

    else:
        message = "🏷<b>Тикер: </b>" + \
                  str(info[0][2]) + "\n🎚<b>Значение: </b>" + \
                  str(info[0][3]) + " " + unit \
                  + "\n📇<b>Режим алерта: </b>" + mode + "\n⏰<b>Тип алерта: </b>Срочный\n" + "⏱<b>Срок действия: </b>" + \
                  date.normalize_date(info[0][8]) + "\n✉️<b>Сообщение: </b>" + str(info[0][5]) + \
                  "\n\n-----------------------------------------------\n<b>Добавлен: </b>" + \
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
            message = message + str(info[n][7]) + "_log\n🏷<b>Тикер: </b>" + \
                      str(info[n][2]) + "\n🎚<b>Значение: </b>" + \
                      str(info[n][3]) + " " + unit \
                      + "\n📇<b>Режим алерта: </b>" + mode + "\n⏰<b>Тип алерта: </b>Бессрочный" + "\n✉️<b>Сообщение: </b>" + \
                      str(info[n][5]) + "\n\n/"

        else:
            message = message + str(info[n][7]) + "_log\n🏷<b>Тикер: </b>" + \
                      str(info[n][2]) + "\n🎚<b>Значение: </b>" + \
                      str(info[n][3]) + " " + unit \
                      + "\n📇<b>Режим алерта: </b>" + mode + "\n⏰<b>Тип алерта: </b>Срочный\n" + "⏱<b>Срок действия: </b>" + \
                      date.normalize_date(info[n][8]) + "\n✉️<b>Сообщение: </b>" + \
                      str(info[n][5]) + "\n\n/"

    return message[0:-1] + "-----------------------------------------------\nДля редактирования алерта нажмите на его номер"

def data_transfer_menu(user_id):
    start = "🏢Наша команда заботится о вас, поэтому, чтобы не переносить информацию о портфелях и алертах на новый аккаунт telegram"\
            "вручную, мы добавили систему ключей переноса. Для того, чтобы перенести информацию на новый аккаунт, вам достаточно"\
            "сгенерировать уникальный ключ и ввести его на новой учетной записи.\n\n<b>❗️Важно знать:</b> \nВведя уникальный ключ на новом"\
            " аккаунте, и, подтвердив действие на старом аккаунте, вся ваша информация перенесется на новый аккаунт, мгновенно удалившись"\
            " на старом\n\n"
    if bool(db.user_token(user_id)):
        token_message = f"🔑У вас уже есть уникальный ключ: {db.user_token(user_id)[0][1]}\n\n*Его можно пересоздать, если понадобится"
    else:
        token_message = ""
    return start + token_message

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
            message = message + str(info[n][7]) + "_note\n🏷<b>Тикер: </b>" + \
                      str(info[n][2]) + "\n🎚<b>Значение: </b>" + \
                      str(info[n][3]) + " " + unit \
                      + "\n📇<b>Режим алерта: </b>" + mode + "\n⏰<b>Тип алерта: </b>Бессрочный" + "\n✉️<b>Сообщение: </b>" + \
                      str(info[n][5]) + "\n\n/"

        else:
            message = message + str(info[n][7]) + "_note\n🏷<b>Тикер: </b>" + \
                      str(info[n][2]) + "\n🎚<b>Значение: </b>" + \
                      str(info[n][3]) + " " + unit \
                      + "\n📇<b>Режим алерта: </b>" + mode + "\n⏰<b>Тип алерта: </b>Срочный\n" + "⏱<b>Срок действия: </b>" + \
                      date.normalize_date(info[n][8]) + "\n✉️<b>Сообщение: </b>" + \
                      str(info[n][5]) + "\n\n/"

    return message[0:-1] + "-----------------------------------------------\nДля редактирования алерта нажмите на его номер"


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
        yahoo_first_link = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}.ME?modules=price", headers=header).content
        yahoo_second_link = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}.ME?modules=assetProfile", headers=header).content
        wallet = "RUB"
        price = str(sm.get_moex_price(ticker)) + " " + wallet

    else:
        yahoo_first_link = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=price", headers=header).content
        yahoo_second_link = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=assetProfile", headers=header).content
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

    message += f"\n-----------------------------------------------\n💰<b>Цена:</b> {price}\n" \
               f"↕️<b>Изменение цены за день:</b> {day_price_change} {wallet} ({day_price_change_percent})\n" \
               f"{sm.ytd_return(ticker)}{sm.dividend(ticker)}\n🏦<b>Биржа:</b> {exchange}\n" \
               f"🔦<b>Направление:</b> {industry}\n⛏<b>Отрасль:</b> {sector}"

    if not "." in ticker and ticker not in tickers.moex_tickers:
        message += f"\n📊<b>Zacks rank:</b> {sm.zacks_rank(ticker)}"
    return message


def my_portfolios(user_id):
    if db.user_has_portfolios(user_id):
        portfolios = db.user_portfolios(user_id)
        message = "<u><b>Мои инвестиционные портфели:</b></u>\n\n/"
        for selected_portfolio in portfolios:
            if db.portfolio_has_stocks(user_id, selected_portfolio[2]) or db.portfolio_has_money(user_id,
                                                                                                 selected_portfolio[2]):
                wallets = db.wallets_in_portfolio(user_id, selected_portfolio[2])
                message += f"{selected_portfolio[2]}_portfolio\n️<b>Название портфеля: </b>{selected_portfolio[3]}\n<b>Всего в портфеле: </b>\n"
                for wallet in wallets:
                    difference = round(float(db.real_sum_by_wallet(user_id, selected_portfolio[2], wallet) - \
                                 db.sum_by_wallet(user_id, selected_portfolio[2], wallet)), 2)
                    if difference == 0:
                        message += "🟡 "
                    if difference < 0:
                        message += "🔴 "
                    if difference > 0:
                        difference = f"+{str(difference)}"
                        message += "🟢 "
                    message += f"{db.real_sum_by_wallet(user_id, selected_portfolio[2], wallet)} ({difference}) {wallet}\n"
                message += "\n/"
            else:
                message += f"{selected_portfolio[2]}_portfolio\n<b>Название портфеля: </b>{selected_portfolio[3]}\n" \
                           f"Портфель пуст\n/"
        return message[:-1] + "-----------------------------------------------\nДля получения подробной информации " \
                              "и редактирования портфеля нажмите на его номер"
    else:
        return "Инвестиционные портфели пока не добавлены"


def portfolio_full_info(user_id, individual_portfolio_id):
    symbol = ""
    money = db.money_from_portfolio(user_id, individual_portfolio_id)
    stocks = db.stocks_from_portfolio(user_id, individual_portfolio_id)
    message = f"<b>💼 {db.portfolio_name(user_id, individual_portfolio_id)}</b>\n\n"
    if db.portfolio_has_money(user_id, individual_portfolio_id) or db.portfolio_has_stocks(user_id,
                                                                                           individual_portfolio_id):
        if db.portfolio_has_stocks(user_id, individual_portfolio_id):
            message += "<u><b>Ценные бумаги:</b></u>\n\n"
            for note in stocks:
                price = sm.price(note[2])
                difference = round(((float(note[5])*float(price))-(float(note[5])*float(note[4]))), 2)
                if difference == 0:
                    symbol = "🟡"
                if difference < 0:
                    symbol = "🔴"
                if difference > 0:
                    difference = f"+{str(difference)}"
                    symbol = "🟢"

                message += f"{symbol}<b>{sm.long_name(note[2])} ({note[2]})</b>\n<b>Цена покупки: </b>{note[4]} {note[3]}\n" \
                           f"<b>Текущая цена: </b>{round(int(price),2)} {note[3]}\n<b>Количество: </b>{note[5]}" \
                           f"\n<u><b>Общая стоимость: </b></u> " \
                           f"{round((float(note[5])*float(price)),2)} ({difference}) {note[3]}\n\n"
            message += "-----------------------------------------------\n"
        if db.portfolio_has_money(user_id, individual_portfolio_id):
            message += "<b>Валюты:</b>\n"
            for note in money:
                message += f"{note[5]} {note[3]}\n"

            message += "-----------------------------------------------\n"
    else:
        message += "Портфель пуст"
    return message


data_transfer_acception = """❗️<b>Получен запрос на перенос данных</b>❗️

Подтверждаете ли вы перенос?

⛔️Если запрос был произведен не вами, незамедлительно сгенерируйте новый уникальный ключ в настройках"""