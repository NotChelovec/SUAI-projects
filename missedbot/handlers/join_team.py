from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from missedbot import bot
from database import crud

from missedbot.handlers.student_keyboard import student_menu_keyboard

@bot.message_handler(func=lambda message: message.text == "Присоединиться к команде")
async def handle_join_team(message: Message):
    user_id = message.from_user.id
    student = crud.get_student_by_telegram_id(user_id)
    disciplines = crud.get_disciplines()
    markup = InlineKeyboardMarkup()
    for discipline in disciplines:
        markup.add(InlineKeyboardButton(discipline.name, callback_data=f"join_team_{discipline.id}"))

    await bot.send_message(message.chat.id, "Выберите дисциплину:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("join_team_"))
async def callback_join_team(call):
    discipline_id = int(call.data.split("_")[2])
    user_id = call.from_user.id
    student = crud.get_student_by_telegram_id(user_id)

    if not student:
        await bot.send_message(call.message.chat.id, "Студент не найден.")
        return
    
    existing_team = crud.get_team_by_student_and_discipline(student.id, discipline_id)
    if existing_team:
        await bot.send_message(call.message.chat.id, f"Вы уже создали команду в этой дисциплине: {existing_team.name}.")
        return
    
    teams = crud.get_open_teams_by_discipline_and_group(discipline_id, student.group_id)
    if not teams:
        await bot.send_message(call.message.chat.id, "Нет доступных команд для присоединения.")
        return
    
    markup = InlineKeyboardMarkup()
    for team in teams:
        markup.add(InlineKeyboardButton(team.name, callback_data=f"join_team_select_{team.id}"))

    await bot.send_message(call.message.chat.id, "Выберите команду:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("join_team_select_"))
async def callback_join_team_select(call):
    team_id = int(call.data.split("_")[2])
    user_id = call.from_user.id
    student = crud.get_student_by_telegram_id(user_id)

    if not student:
        await bot.send_message(call.message.chat.id, "Студент не найден.")
        return
    
    team = crud.get_team_by_id(team_id)
    if not team.is_open:
        await bot.send_message(call.message.chat.id, "Набор в команду закрыт.")
        return
    
    crud.join_team(team.id, student.id)
    await bot.send_message(call.message.chat.id, f"Вы успешно присоединились к команде {team.name}.", reply_markup=student_menu_keyboard())
    print(f"Студент {student.full_name} успешно присоединился к команде {team.name}.")  # Логирование
