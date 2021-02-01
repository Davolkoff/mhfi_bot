import sqlite3  # библиотека для работа с базами данных
import sm_info as sm  # файл с функциями, связанными с биржей
from date import normal_now  # функция получения текущего времени


class Database:
    # подключение к БД, инициализация класса
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    # добавление нового алерта
    def add_alert(self, user_id, ticker, mode, value, message, date, add_date):
        with self.connection:
            if mode == "reaching" and float(sm.price(ticker)) <= float(value):
                mode = ">="
            if mode == "reaching" and float(sm.price(ticker)) > float(value):
                mode = "<="
            alert_id = Database.last_alert_id(self) + 1
            individual_alert_id = Database.last_individual_alert_id(self, user_id) + 1
            return self.cursor.execute("INSERT INTO `alerts` (`alert_id`, `user_id`, `ticker`, `mode`, `value`, "
                                       "`message`, `status`, `individual_alert_id`, `date`, `add_date`, `edit_date`) "
                                       "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                                       (alert_id, user_id, ticker, mode, value, message, True, individual_alert_id,
                                        date, add_date, "4000-01-01"))

    # удаление алерта
    def delete_alert(self, owner, individual):
        with self.connection:
            return self.cursor.execute("DELETE FROM `alerts` WHERE `user_id` = ? AND individual_alert_id = ?",
                                       (owner, individual))

    # получение id последнего алерта
    def last_alert_id(self):
        try:
            with self.connection:
                return self.cursor.execute("SELECT * FROM `alerts` ORDER BY alert_id DESC").fetchone()[0]
        except:
            return 0

    # получение индивидульного id последнего алерта
    def last_individual_alert_id(self, user_id):
        try:
            with self.connection:
                return self.cursor.execute("SELECT * FROM `alerts` WHERE `user_id` = ? ORDER BY individual_alert_id "
                                           "DESC", (user_id,)).fetchone()[0]
        except:
            return 0

    # отключение алерта
    def alert_off(self, owner, individual):
        Database.add_alert_execute_date(self, owner, individual)
        with self.connection:
            return self.cursor.execute("UPDATE `alerts` SET `status` = ? WHERE `user_id` = ? AND "
                                       "individual_alert_id = ?", (False, owner, individual))

    # изменение тикера в алерте
    def alert_change_ticker(self, ticker, owner, individual):
        with self.connection:
            return self.cursor.execute("UPDATE `alerts` SET `ticker` = ? WHERE `user_id` = ? AND "
                                       "individual_alert_id = ?", (ticker, owner, individual))

    # изменение режима и значения в алерте
    def alert_change_mode_and_value(self, mode, value, owner, individual):

        with self.connection:
            return self.cursor.execute("UPDATE `alerts` SET `mode` = ?, `value` = ? WHERE `user_id` = ? AND "
                                       "individual_alert_id = ?", (mode, value, owner, individual))

    # изменение сообщения в алерте
    def alert_change_message(self, message, owner, individual):
        with self.connection:
            return self.cursor.execute("UPDATE `alerts` SET `message` = ? WHERE `user_id` = ? AND "
                                       "individual_alert_id = ?", (message, owner, individual))

    # изменение времени действия алерта
    def alert_change_time(self, time, owner, individual):
        with self.connection:
            return self.cursor.execute("UPDATE `alerts` SET `date` = ?  WHERE `user_id` = ? AND "
                                       "individual_alert_id = ?", (time, owner, individual))

    # получение активных алертов
    def get_active_alerts(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `alerts` WHERE `status` = 1").fetchall()

    # получение уникальных тикеров из списка активных алертов
    def get_unique_tickers(self):
        with self.connection:
            list_of_tickers = []
            for i in range(len(Database.get_active_alerts(self))):
                list_of_tickers.append(Database.get_active_alerts(self)[i][2])
            return list(set(list_of_tickers))

    # получение алертов с определенным тикером
    def find_active_alerts_by_ticker(self, ticker):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `alerts` WHERE `ticker` = ? AND `status` = ?",
                                       (ticker, True)).fetchall()

    # вывод активных алертов
    def active_alerts_list(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `alerts` WHERE `user_id` = ? "
                                       "AND `status` = ?", (user_id, True)).fetchall()

    # вывод выполненных алертов
    def executed_alerts_list(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `alerts` WHERE `user_id` = ? "
                                           "AND `status` = ?", (user_id, False)).fetchall()

    # проверка наличия email в базе данных
    def mail_exists(self, user_id):
        with self.connection:
            return bool(len(self.cursor.execute("SELECT * FROM `mail` WHERE `user_id` = ?", (user_id,)).fetchall()))

    # добавление почты
    def add_mail(self, user_id, mail):
        with self.connection:
            return self.cursor.execute("INSERT INTO `mail` (`user_id`, `mail`) VALUES(?,?)", (user_id, mail))

    # изменение почты
    def change_mail(self, user_id, mail):
        with self.connection:
            return self.cursor.execute("UPDATE `mail` SET `mail` = ? WHERE `user_id` = ?",
                                       (mail, user_id))

    # проверка подписки пользователя на email алерты
    def is_on_email_alert(self, user_id):
        with self.connection:
            try:
                return bool(self.cursor.execute("SELECT * FROM `settings` WHERE user_id = ?", (user_id,)).fetchall()[0][1])
            except:
                return False

    # получение почты пользователя из базы данных
    def get_email(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `mail` WHERE user_id = ?", (user_id,)).fetchall()[0][1]

    # проверка, есть ли юзер в настройках
    def user_exists(self, user_id):
        with self.connection:
            return bool(len(self.cursor.execute("SELECT * FROM `settings` WHERE `user_id` = ?", (user_id,)).fetchall()))

    # добавление юзера в настройки
    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO `settings` (`user_id`) VALUES(?)", (user_id,))

    # включение дублирования алерта на почту
    def alert_mail_on(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `settings` SET `mail_alert` = ? WHERE `user_id` = ?",
                                       (True, user_id))

    # выключение дублирования алерта на почту
    def alert_mail_off(self, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `settings` SET `mail_alert` = ? WHERE `user_id` = ?",
                                       (False, user_id))

    # получение информации об алерте по его id
    def alert_info_by_individual_id(self, owner, individual):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `alerts` WHERE individual_alert_id = ? AND `user_id` = ?",
                                       (individual, owner)).fetchall()

    # добавление даты отключения алерта по его id
    def add_alert_execute_date(self, owner, individual):
        with self.connection:
            return self.cursor.execute("UPDATE `alerts` SET `execute_date` = ? WHERE `individual_alert_id` = ? "
                                       "AND `user_id` = ?",
                                       (normal_now(), individual, owner))

    # добавление даты последнего изменения алерта
    def add_alert_edit_date(self, owner, individual):
        with self.connection:
            return self.cursor.execute("UPDATE `alerts` SET `edit_date` = ? WHERE `individual_alert_id` = ? "
                                       "AND `user_id` = ?",
                                       (normal_now(), individual, owner))

    # активация алерта по id
    def activate_alert_by_id(self, owner, individual):
        with self.connection:
            return self.cursor.execute("UPDATE `alerts` SET `status` = ?, `execute_date` = ? "
                                       "WHERE `individual_alert_id` = ? AND `user_id` = ?",
                                       (True, None, individual, owner))

    # проверка, существует ли такое название инвестиционного портфеля
    def portfolio_name_exists(self, user_id, name):
        with self.connection:
            return bool(len(self.cursor.execute("SELECT * FROM `portfolios` WHERE `user_id` = ? "
                                                "AND `portfolio_name` = ?", (user_id, name)).fetchall()))

    # получение id последнего портфеля
    def last_portfolio_id(self, user_id):
        try:
            with self.connection:
                return self.cursor.execute("SELECT * FROM `portfolios` WHERE `user_id` = ? ORDER BY portfolio_id "
                                           "DESC", (user_id,)).fetchone()[1]
        except:
            return 0

    # получение индивидульного id последнего портфеля
    def last_individual_portfolio_id(self, user_id):
        try:
            with self.connection:
                return self.cursor.execute("SELECT * FROM `portfolios` WHERE `user_id` = ? ORDER BY "
                                           "individual_portfolio_id DESC", (user_id,)).fetchone()[2]
        except:
            return 0

    # добавление портфеля
    def add_portfolio(self, user_id, portfolio_name):
        individual_id = Database.last_individual_portfolio_id(self, user_id) + 1
        portfolio_id = Database.last_portfolio_id(self, user_id) + 1
        with self.connection:
            return self.cursor.execute("INSERT INTO `portfolios` (`user_id`, `portfolio_id`, "
                                       "`individual_portfolio_id`, `portfolio_name`) "
                                       "VALUES(?,?,?,?)",
                                       (user_id, portfolio_id, individual_id, portfolio_name))

    # проверка наличия портфелей у пользователя
    def user_has_portfolios(self, user_id):
        with self.connection:
            return bool(len(self.cursor.execute("SELECT * FROM `portfolios` WHERE user_id = ?", (user_id,)).fetchall()))

    # получение портфелей, принадлежащих пользователю
    def user_portfolios(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `portfolios` WHERE user_id = ?", (user_id,)).fetchall()

    # получение валют, находящихся в портфеле
    def portfolio_wallets(self, user_id, individual_portfolio_id):
        with self.connection:
            wallets = []
            message = ""
            portfolios = self.cursor.execute("SELECT * FROM `stocks_notes` WHERE `individual_portfolio_id` = ? AND "
                                             "`user_id` = ?", (individual_portfolio_id, user_id)).fetchall()
            for selected_portfolio in portfolios:
                wallets.append(selected_portfolio[3])
            for wallet in list(set(wallets)):
                message += wallet + ", "
            return message[:-2]

    # проверка, есть ли в портфеле бумаги
    def portfolio_has_stocks(self, user_id, individual_portfolio_id):
        with self.connection:
            return bool(len(self.cursor.execute("SELECT * FROM `stocks_notes` WHERE `individual_portfolio_id` = ? AND "
                                                "`user_id` = ? AND NOT `ticker` = ?", (individual_portfolio_id, user_id,
                                                                                       "money")).fetchall()))

    # проверка, есть ли в портфеле бумаги
    def portfolio_has_money(self, user_id, individual_portfolio_id):
        with self.connection:
            return bool(len(self.cursor.execute("SELECT * FROM `stocks_notes` WHERE `individual_portfolio_id` = ? AND "
                                        "`user_id` = ? AND `ticker` = ?", (individual_portfolio_id, user_id,
                                                                               "money")).fetchall()))

    # удаление портфеля
    def delete_portfolio(self, user_id, individual_portfolio_id):
        with self.connection:
            self.cursor.execute("DELETE  FROM `stocks_notes` WHERE `user_id` = ? AND `individual_portfolio_id` = ?",
                                (user_id, individual_portfolio_id))
            return self.cursor.execute("DELETE  FROM `portfolios` WHERE `user_id` = ? AND `individual_portfolio_id` "
                                       "= ?", (user_id, individual_portfolio_id))

    # проверка, есть ли такая бумага у пользователя в этом портфеле
    def ticker_exists_in_portfolio(self, user_id, individual_portfolio_id, ticker):
        with self.connection:
            return bool(len(self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                                    "`individual_portfolio_id` = ? AND `ticker` = ?",
                                                    (user_id, individual_portfolio_id, ticker)).fetchall()))

    # добавление бумаги в портфель
    def add_stock(self, user_id, individual_portfolio_id, ticker, currency, value):
        if Database.ticker_exists_in_portfolio(self, user_id, individual_portfolio_id, ticker):
            with self.connection:
                stock_info = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                                     "`individual_portfolio_id` = ? AND `ticker` = ?",
                                                     (user_id, individual_portfolio_id, ticker)).fetchall()
                edited_value = int(stock_info[0][5]) + int(value)
                edited_currency = round((float(stock_info[0][4])*float(stock_info[0][5]) + float(currency)*float(value)) / float(edited_value), 2)
                return self.connection.execute("UPDATE `stocks_notes` SET `currency` = ?, `value` = ? WHERE "
                                               "`user_id` = ? AND `individual_portfolio_id` = ? AND `ticker` = ?",
                                               (edited_currency, edited_value, user_id, individual_portfolio_id, ticker))
        else:
            with self.connection:
                return self.connection.execute("INSERT INTO `stocks_notes` (user_id, individual_portfolio_id, ticker, "
                                               "wallet, currency, value) VALUES(?,?,?,?,?,?)",
                                               (user_id, individual_portfolio_id, ticker, sm.wallet(ticker),
                                                currency, value))

    # удаление бумаги из портфеля
    def del_stock(self, user_id, individual_portfolio_id, ticker, currency, value):
        if int(Database.number_of_stocks_in_portfolio(self, user_id, individual_portfolio_id, ticker)) == int(value):
            with self.connection:
                return self.cursor.execute("DELETE FROM `stocks_notes` WHERE `user_id` = ? AND "
                                           "individual_portfolio_id = ? AND `ticker` = ?",
                                           (user_id, individual_portfolio_id, ticker))
        else:
            stock_info = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                                 "`individual_portfolio_id` = ? AND `ticker` = ?",
                                                 (user_id, individual_portfolio_id, ticker)).fetchall()
            edited_value = int(stock_info[0][5]) - int(value)
            with self.connection:
                return self.connection.execute("UPDATE `stocks_notes` SET `value` = ? WHERE "
                                               "`user_id` = ? AND `individual_portfolio_id` = ? AND `ticker` = ?",
                                               (edited_value, user_id, individual_portfolio_id, ticker))

    # получение количества бумаг по тикеру в портфеле
    def number_of_stocks_in_portfolio(self, user_id, individual_portfolio_id, ticker):
        with self.connection:
            return self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                           "`individual_portfolio_id` = ? AND `ticker` = ?",
                                           (user_id, individual_portfolio_id, ticker)).fetchall()[0][5]

    # получение количества денег по валюте в портфеле
    def number_of_money_in_portfolio(self, user_id, individual_portfolio_id, wallet):
        with self.connection:
            return self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                           "`individual_portfolio_id` = ? AND `ticker` = ? AND `wallet` = ?",
                                           (user_id, individual_portfolio_id, "money", wallet)).fetchall()[0][5]

    # добавление денег в портель
    def add_money(self, user_id, individual_portfolio_id, wallet, value):
        if Database.wallet_exists_in_portfolio(self, user_id, individual_portfolio_id, "money", wallet):
            with self.connection:
                stock_info = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                                     "`individual_portfolio_id` = ? AND `ticker` = ? AND `wallet` = ?",
                                                     (user_id, individual_portfolio_id, "money", wallet)).fetchall()
                edited_value = float(stock_info[0][4]) + float(value)
                return self.connection.execute("UPDATE `stocks_notes` SET `currency` = ? WHERE `user_id` = ? AND "
                                               "`individual_portfolio_id` = ? AND `ticker` = ? AND `wallet` = ?",
                                               (edited_value, user_id, individual_portfolio_id, "money", wallet))
        else:
            with self.connection:
                return self.connection.execute("INSERT INTO `stocks_notes` (user_id, individual_portfolio_id, ticker, "
                                               "wallet, currency, value) VALUES(?,?,?,?,?,?)",
                                               (user_id, individual_portfolio_id, "money", wallet, value, "0"))

    # проверка, какие валюты есть в портфеле
    def wallets_in_portfolio(self, user_id, individual_portfolio_id):
        wallets = []
        with self.connection:
            notes = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                            "`individual_portfolio_id` = ?",
                                            (user_id, individual_portfolio_id))
            for selected_wallet in notes:
                wallets.append(selected_wallet[3])
            return list(set(wallets))

    # проверка, деньги каких валют есть в портфеле
    def money_wallets_in_portfolio(self, user_id, individual_portfolio_id):
        wallets = []
        with self.connection:
            notes = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                            "`individual_portfolio_id` = ? AND `ticker` = ?",
                                            (user_id, individual_portfolio_id, "money"))
            for selected_wallet in notes:
                wallets.append(selected_wallet[3])
            return list(set(wallets))

    # проверка, акции каких валют есть в портфеле
    def stocks_wallets_in_portfolio(self, user_id, individual_portfolio_id):
        wallets = []
        with self.connection:
            notes = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                            "`individual_portfolio_id` = ? AND NOT `ticker` = ?",
                                            (user_id, individual_portfolio_id, "money"))
            for selected_wallet in notes:
                wallets.append(selected_wallet[3])
            return list(set(wallets))

    # удаление денег из портфеля
    def del_money(self, user_id, individual_portfolio_id, wallet, value):
        if float(Database.number_of_money_in_portfolio(self, user_id, individual_portfolio_id, wallet)) == float(
                value):
            with self.connection:
                return self.cursor.execute("DELETE FROM `stocks_notes` WHERE `user_id` = ? AND "
                                           "individual_portfolio_id = ? AND `ticker` = ? AND `wallet` = ?",
                                           (user_id, individual_portfolio_id, "money", wallet))
        else:
            stock_info = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                                 "`individual_portfolio_id` = ? AND `ticker` = ? AND `wallet` = ?",
                                                 (user_id, individual_portfolio_id, "money", wallet)).fetchall()
            edited_value = float(stock_info[0][4]) - float(value)
            with self.connection:
                return self.connection.execute("UPDATE `stocks_notes` SET `currency` = ? WHERE "
                                               "`user_id` = ? AND `individual_portfolio_id` = ? AND `wallet` = ?",
                                               (edited_value, user_id, individual_portfolio_id, wallet))

    # получение названия портфеля
    def portfolio_name(self, user_id, individual_portfolio_id):
        with self.connection:
            return self.connection.execute("SELECT * FROM `portfolios` WHERE `user_id` = ? AND "
                                           "`individual_portfolio_id` = ?", (user_id, individual_portfolio_id)).fetchall()[0][3]

    # получение информации о бумагах из портфеля
    def stocks_from_portfolio(self, user_id, individual_portfolio_id):
        with self.connection:
            return self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                           "`individual_portfolio_id` = ? AND NOT `ticker` = ?",
                                           (user_id, individual_portfolio_id, "money")).fetchall()

    # получение информации о валютах из портфеля
    def money_from_portfolio(self, user_id, individual_portfolio_id):
        with self.connection:
            return self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                           "`individual_portfolio_id` = ? AND `ticker` = ?",
                                           (user_id, individual_portfolio_id, "money")).fetchall()

    # проверка, есть ли такая валюта у пользователя в этом портфеле
    def wallet_exists_in_portfolio(self, user_id, individual_portfolio_id, ticker, wallet):
        with self.connection:
            return bool(len(self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                                    "`individual_portfolio_id` = ? AND `ticker` = ? AND `wallet` = ?",
                                                    (user_id, individual_portfolio_id, ticker, wallet)).fetchall()))

    # получение сумма значений из портфеля по валюте
    def sum_by_wallet(self, user_id, individual_portfolio_id, wallet):
        sum = 0
        with self.connection:
            stocks_notes = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                                   "`individual_portfolio_id` = ? AND `wallet` = ? AND NOT `ticker` = ?",
                                                   (user_id, individual_portfolio_id, wallet, "money"))
            money_notes = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                                  "`individual_portfolio_id` = ? AND `wallet` = ? AND `ticker` = ?",
                                                  (user_id, individual_portfolio_id, wallet, "money"))
        for note in stocks_notes:
            sum += (float(note[5]) * float(note[4]))
        for note in money_notes:
            sum += (float(note[4]))
        return round(sum, 2)

    # получение стоимости портфеля, опираясь на реальные значения ценных бумаг
    def real_sum_by_wallet(self, user_id, individual_portfolio_id, wallet):
        sum = 0
        with self.connection:
            stocks_notes = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                                   "`individual_portfolio_id` = ? AND `wallet` = ? AND NOT `ticker` = ?",
                                                   (user_id, individual_portfolio_id, wallet, "money"))
            money_notes = self.connection.execute("SELECT * FROM `stocks_notes` WHERE `user_id` = ? AND "
                                                  "`individual_portfolio_id` = ? AND `wallet` = ? AND `ticker` = ?",
                                                  (user_id, individual_portfolio_id, wallet, "money"))
        for note in stocks_notes:
            sum += (float(note[5]) * float(sm.price(note[2])))
        for note in money_notes:
            sum += (float(note[4]))
        return round(sum, 2)

    # переименование портфеля
    def rename_portfolio(self, name, user_id, individual_portfolio_id):
        with self.connection:
            return self.connection.execute("UPDATE `portfolios` SET `portfolio_name` = ? WHERE `user_id` = ? AND "
                                           "`individual_portfolio_id` = ?", (name, user_id, individual_portfolio_id))

    # закрытие соединения с БД
    def close(self):
        self.connection.close()
