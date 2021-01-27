import keyboards as kb
from keyboards import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup  # машина состояний
from aiogram.dispatcher import FSMContext  # машина состояний
import messages
from aiogram import types
import mail
import random

code = ""  # сюда сохраняется код для подтверждения электронной почты
i = 0  # это счётчик неудачных попыток ввода кода, присланного на почту


# состояния для добавления или изменения адреса электронной почты
class EmailChange(StatesGroup):
    email = State()
    check = State()


# функция для изменения меню настроек в зависимости от выбранных параметров пользователя
async def change_settings_keyboard(user_id):
    if db.is_on_email_alert(user_id):
        kb.mail_alert = InlineKeyboardButton("Дублировать алерт на электронную почту: ВКЛ",
                                             callback_data='mail_alert')
    else:
        kb.mail_alert = InlineKeyboardButton("Дублировать алерт на электронную почту: ВЫКЛ",
                                             callback_data='mail_alert')
    if db.mail_exists(user_id):
        kb.add_mail = InlineKeyboardButton("Изменить адрес электронной почты", callback_data='add_mail')
    else:
        kb.add_mail = InlineKeyboardButton("Добавить адрес электронной почты", callback_data='add_mail')
    kb.settings_menu = InlineKeyboardMarkup(row_width=1).add(kb.mail_alert, kb.add_mail, kb.backToMainMenu)


@dp.callback_query_handler(lambda call: call.data == "add_mail")
async def add_mail(call):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=messages.email_enter,
                                reply_markup=kb.toSettings)
    await EmailChange.email.set()


@dp.callback_query_handler(lambda call: call.data == "mail_alert")
async def mail_alert(call):
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
                                                     "\nОсталось попыток: " + str(4-i))
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


# обработчик кнопки "назад" при добавлении электронной почты
@dp.callback_query_handler(lambda call: True, state="*")
async def back_to_settings_menu(call, state: FSMContext):
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
