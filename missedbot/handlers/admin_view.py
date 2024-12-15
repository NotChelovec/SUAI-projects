
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from missedbot import bot
from database import crud
from missedbot.handlers.admin_keyboard import admin_menu_keyboard
from telebot.asyncio_handler_backends import State, StatesGroup

class AdminStates(StatesGroup):
    AWAITING_STUDENT_COMMENT = State()
    AWAITING_TEACHER_COMMENT = State()

@bot.message_handler(func=lambda message: message.text == "Отчёты студентов")
async def handle_view_reports(message: Message):
    try:
        print("Starting handle_view_reports")
        disciplines = crud.get_unique_disciplines()
        print(f"Disciplines loaded: {disciplines}")

        markup = InlineKeyboardMarkup()
        for discipline in disciplines:
            markup.add(InlineKeyboardButton(discipline['name'], callback_data=f"view_reports_discipline_{discipline['name']}"))
            print(f"Added discipline to markup: {discipline['name']}")

        await bot.send_message(message.chat.id, "Выберите дисциплину:", reply_markup=markup)
        print("Discipline selection sent to user")
    except Exception as e:
        await bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
        print(f"Error in handle_view_reports: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("view_reports_discipline_"))
async def callback_view_reports_discipline(call):
    discipline_name = call.data.split("_")[-1]
    try:
        print(f"Discipline: {discipline_name}")
        groups = crud.get_groups_by_discipline(discipline_name)
        print(f"Groups loaded for discipline {discipline_name}: {groups}")

        if not groups:
            await bot.send_message(call.message.chat.id, "Группы не найдены для этой дисциплины.")
            return
        
        markup = InlineKeyboardMarkup()
        for group in groups:
            print(f"Adding group to markup: {group['name']}")  # Добавим отладочное сообщение
            markup.add(InlineKeyboardButton(group['name'], callback_data=f"view_reports_group_{group['name']}_{discipline_name}"))

        await bot.send_message(call.message.chat.id, "Выберите группу:", reply_markup=markup)
        print("Group selection sent to user")
    except Exception as e:
        await bot.send_message(call.message.chat.id, f"Произошла ошибка: {e}")
        print(f"Error in callback_view_reports_discipline: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("view_reports_group_"))
async def callback_view_reports_group(call):
    parts = call.data.split("_")
    group_name = parts[-2]
    discipline_name = parts[-1]
    try:
        print(f"Group: {group_name}, Discipline: {discipline_name}")
        teams = crud.get_teams_by_group(group_name, discipline_name)
        print(f"Teams loaded for group {group_name} and discipline {discipline_name}: {teams}")

        if not teams:
            await bot.send_message(call.message.chat.id, "Команды не найдены для этой группы.")
            return
        
        markup = InlineKeyboardMarkup()
        for team in teams:
            print(f"Adding team to markup: {team.name}")  # Добавим отладочное сообщение
            markup.add(InlineKeyboardButton(team.name, callback_data=f"view_report_{team.id}"))

        await bot.send_message(call.message.chat.id, "Выберите команду:", reply_markup=markup)
        print("Team selection sent to user")
    except Exception as e:
        await bot.send_message(call.message.chat.id, f"Произошла ошибка: {e}")
        print(f"Error in callback_view_reports_group: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("view_report_"))
async def callback_view_report(call):
    team_id = int(call.data.split("_")[-1])
    try:
        print(f"Team ID: {team_id}")
        team = crud.get_team_by_id(team_id)
        if not team:
            await bot.send_message(call.message.chat.id, "Команда не найдена.")
            return

        report = team.reports if team.reports else "Отчет отсутствует."
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Комментарий для студента", callback_data=f"add_comment_student_{team.id}"))
        markup.add(InlineKeyboardButton("Комментарий для преподавателя", callback_data=f"add_comment_teacher_{team.id}"))

        await bot.send_message(call.message.chat.id, f"Отчет команды {team.name}:\n{report}", reply_markup=markup)
        print("Report sent to user")
    except Exception as e:
        await bot.send_message(call.message.chat.id, f"Произошла ошибка: {e}")
        print(f"Error in callback_view_report: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_comment_student_"))
async def callback_add_comment_student(call):
    team_id = int(call.data.split("_")[-1])
    await bot.send_message(call.message.chat.id, "Введите комментарий для студента:")
    await bot.set_state(call.from_user.id, AdminStates.AWAITING_STUDENT_COMMENT, call.message.chat.id)
    
    async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['team_id'] = team_id

@bot.message_handler(state=AdminStates.AWAITING_STUDENT_COMMENT)
async def process_student_comment(message: Message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        team_id = data['team_id']
    comment = message.text
    crud.update_team_comment(team_id, comment, "student")
    await bot.send_message(message.chat.id, "Комментарий для студента добавлен.")
    await bot.delete_state(message.from_user.id, message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_comment_teacher_"))
async def callback_add_comment_teacher(call):
    team_id = int(call.data.split("_")[-1])
    await bot.send_message(call.message.chat.id, "Введите комментарий для преподавателя:")
    await bot.set_state(call.from_user.id, AdminStates.AWAITING_TEACHER_COMMENT, call.message.chat.id)
    
    async with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['team_id'] = team_id

@bot.message_handler(state=AdminStates.AWAITING_TEACHER_COMMENT)
async def process_teacher_comment(message: Message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        team_id = data['team_id']
    comment = message.text
    crud.update_team_comment(team_id, comment, "teacher")
    await bot.send_message(message.chat.id, "Комментарий для преподавателя добавлен.")
    await bot.delete_state(message.from_user.id, message.chat.id)
