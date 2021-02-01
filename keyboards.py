from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# стандартные кнопки возврата
backToMainMenu = InlineKeyboardButton('⬅ Главное меню', callback_data='main_menu_button')
backToAlMenu = InlineKeyboardButton('⬅ Меню алертов', callback_data='alerts')

# инициализация клавиатуры главного меню
my_portfolios = InlineKeyboardButton('💼Мои инвестиционные портфели', callback_data='my_portfolios')
info = InlineKeyboardButton('📑Информация о ценной бумаге', callback_data='info')
alerts = InlineKeyboardButton('🚨Алерты', callback_data='alerts')
about_us = InlineKeyboardButton('🎩О нас', callback_data='about_us')
feedback = InlineKeyboardButton('☎️Обратная связь', callback_data='feedback')
settings = InlineKeyboardButton('🛠Настройки', callback_data='settings')
mainMenu = InlineKeyboardMarkup(row_width=1).add(my_portfolios, info, alerts, about_us, feedback, settings)


# инициализация меню алертов
active_alerts = InlineKeyboardButton('Активные алерты', callback_data='active_alerts')
executed_alerts = InlineKeyboardButton('Выполненные алерты', callback_data='executed_alerts')
add_alert = InlineKeyboardButton('Создать новый алерт', callback_data='add_alert')
alMenu = InlineKeyboardMarkup(row_width=1).add(active_alerts, executed_alerts, add_alert, backToMainMenu)

# меню активных и выполненных алертов
univAlMenu = InlineKeyboardMarkup(row_width=1).add(backToAlMenu, backToMainMenu)

# инициализация меню моего инвестиционного портфеля
add_portfolio = InlineKeyboardButton('Создать инвестиционный портфель', callback_data='add_portfolio')
my_portfolios_menu = InlineKeyboardMarkup(row_width=1).add(add_portfolio, backToMainMenu)

# инициализация меню выбора режима алертов
reaching = InlineKeyboardButton('Достижение цены', callback_data='reaching')
increased_vol = InlineKeyboardButton('Повышенный дневной объём (%)', callback_data='increased_vol')
day_increase = InlineKeyboardButton('Внутридневное движение цены вверх', callback_data='day_increase')
day_decrease = InlineKeyboardButton('Внутридневное движение цены вниз', callback_data='day_decrease')
day_increase_percent = InlineKeyboardButton('Внутридневное движение цены вверх (%)',
                                            callback_data='day_increase_percent')
day_decrease_percent = InlineKeyboardButton('Внутридневное движение цены вниз (%)',
                                            callback_data='day_decrease_percent')
mode_select = InlineKeyboardMarkup(row_width=1).add(reaching, increased_vol, day_increase, day_decrease,
                                                    day_increase_percent, day_decrease_percent)

# инициализация меню обратной связи
feedback_menu = InlineKeyboardMarkup(row_width=1).add(backToMainMenu)

# инициализация клавиатуры подтверждения добавления алерта
accept = InlineKeyboardButton('Подтвердить', callback_data='accept')
edit_alert = InlineKeyboardButton('Заполнить заново', callback_data='edit_alert')
cancel = InlineKeyboardButton('Отмена', callback_data='cancel')
alert_accept_menu = InlineKeyboardMarkup(row_width=1).add(accept, edit_alert, cancel)


# инициализация клавиатуры подтверждения добавления ценной бумаги
edit_stock = InlineKeyboardButton('Заполнить заново', callback_data='edit_stock')
stock_accept_menu = InlineKeyboardMarkup(row_width=1).add(accept, edit_stock, cancel)


# инициализация клавиатуры подтверждения добавления денег в портфель
edit_money = InlineKeyboardButton('Заполнить заново', callback_data='edit_money')
money_accept_menu = InlineKeyboardMarkup(row_width=1).add(accept, edit_money, cancel)


# инициализация клавиатуры с выбором типа алерта
definite = InlineKeyboardButton('Срочный', callback_data='definite')
indefinite = InlineKeyboardButton('Бессрочный', callback_data='indefinite')
time_menu = InlineKeyboardMarkup(row_width=1).add(definite, indefinite)


# инициализация клавиатуры с главным меню
main_menu_button = InlineKeyboardButton("Главное меню", callback_data='main_menu_button')
standart_kb = InlineKeyboardMarkup().add(main_menu_button)


# инициализация меню настроек
mail_alert = InlineKeyboardButton("🔕Дублировать алерт на электронную почту: ВЫКЛ", callback_data='mail_alert')
add_mail = InlineKeyboardButton("Добавить адрес электронной почты", callback_data='add_mail')
settings_menu = InlineKeyboardMarkup(row_width=1).add(mail_alert, add_mail, backToMainMenu)

# клавиатура для возвращения к настройкам
backToSettingsMenu = InlineKeyboardButton("⬅ В настройки", callback_data="backToSettingsMenu")
toSettings = InlineKeyboardMarkup().add(backToSettingsMenu)

# инициализация меню редактирования активного алерта
edit_ticker = InlineKeyboardButton('Редактировать тикер', callback_data='edit_ticker')
edit_mode_and_value = InlineKeyboardButton('Редактировать режим и значение', callback_data='edit_mode_and_value')
edit_time = InlineKeyboardButton('Редактировать время действия', callback_data='edit_time')
edit_message = InlineKeyboardButton('Редактировать сообщение', callback_data='edit_message')
delete_alert = InlineKeyboardButton('Удалить алерт', callback_data='delete_alert')
off_alert = InlineKeyboardButton('Отключить алерт', callback_data='off_alert')
back_to_active_alerts = InlineKeyboardButton('⬅ Назад', callback_data='active_alerts')
edit_active_alert_menu = InlineKeyboardMarkup(row_width=1).add(edit_ticker, edit_mode_and_value, edit_time,
                                                               edit_message, off_alert, delete_alert,
                                                               back_to_active_alerts)


# инициализация меню редактирования выполненного алерта
reactivate_alert = InlineKeyboardButton('🚨Активировать алерт', callback_data='reactivate_alert')
delete_alert = InlineKeyboardButton('❌Удалить алерт', callback_data='delete_alert')
back_to_executed_alerts = InlineKeyboardButton('⬅ Назад', callback_data='executed_alerts')
edit_executed_alert_menu = InlineKeyboardMarkup(row_width=1).add(reactivate_alert, delete_alert,
                                                                 back_to_executed_alerts)


# инициализация меню подтверждения удаления
delete_menu = InlineKeyboardMarkup(row_width=1).add(accept, cancel)


# инициализация меню редактирования портфеля
add_stock = InlineKeyboardButton('🟢⚖️Купить ценную бумагу', callback_data='add_stock')
del_stock = InlineKeyboardButton('🔴⚖️Продать ценную бумагу', callback_data='del_stock')
add_dividend = InlineKeyboardButton('🟢💸Добавить дивиденд', callback_data='add_dividend')
del_dividend = InlineKeyboardButton('🔴💸Удалить дивиденд', callback_data='del_dividend')
add_money = InlineKeyboardButton('🟢💰Внести деньги', callback_data='add_money')
del_money = InlineKeyboardButton('🔴💰Забрать деньги', callback_data='del_money')
delete_portfolio = InlineKeyboardButton('❌Удалить инвестиционный портфель', callback_data='delete_portfolio')
back_to_my_portfolios = InlineKeyboardButton('⬅ Инвестиционные портфели', callback_data='my_portfolios')
edit_portfolio_menu = InlineKeyboardMarkup().add(add_stock, del_stock).add(add_dividend, del_dividend).add(add_money,
                                                                                                           del_money).\
    add(delete_portfolio).add(back_to_my_portfolios).add(backToMainMenu)


# инициализация клавиатуры с выбором валют
usd_wallet = InlineKeyboardButton("USD", callback_data='usd_wallet')
rub_wallet = InlineKeyboardButton("RUB", callback_data='rub_wallet')
eur_wallet = InlineKeyboardButton("EUR", callback_data='eur_wallet')
wallet_menu = InlineKeyboardMarkup(row_width=3).add(usd_wallet, rub_wallet, eur_wallet)


def adaptive_wallet_keyboard(wallets):
    adaptive_wallet_menu = InlineKeyboardMarkup()
    if "USD" in wallets:
        adaptive_wallet_menu.add(usd_wallet)
    if "RUB" in wallets:
        adaptive_wallet_menu.add(rub_wallet)
    if "EUR" in wallets:
        adaptive_wallet_menu.add(eur_wallet)
    return adaptive_wallet_menu
