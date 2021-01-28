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
    def portfolio_name_exists(self, name):
        with self.connection:
            return bool(self.cursor.execute("SELECT * FROM `portfolios` WHERE `portfolio_name` = ?", (name,)))

    # получение id последнего портфеля
    def last_portfolio_id(self, user_id):
        try:
            with self.connection:
                return self.cursor.execute("SELECT * FROM `portfolios` WHERE `user_id` = ? ORDER BY portfolio_id "
                                           "DESC", (user_id,)).fetchone()[0]
        except:
            return 0

    # получение индивидульного id последнего портфеля
    def last_individual_portfolio_id(self, user_id):
        try:
            with self.connection:
                return self.cursor.execute("SELECT * FROM `portfolios` WHERE `user_id` = ? ORDER BY "
                                           "individual_portfolio_id DESC", (user_id,)).fetchone()[0]
        except:
            return 0

    # добавление портфеля
    def add_portfolio(self, user_id, portfolio_name):
        individual_id = Database.last_individual_portfolio_id(self, user_id) + 1
        portfolio_id = Database.last_portfolio_id(self, user_id) + 1
        with self.connection:
            return self.cursor.execute("INSERT INTO `portfolios` (`user_id`, `portfolio_id`, "
                                       "`individual_portfolio_id`, `portfolio_name`) VALUES(?,?,?,?,?)",
                                       (user_id, portfolio_id, individual_id, portfolio_name))

    # закрытие соединения с БД
    def close(self):
        self.connection.close()
