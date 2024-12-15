from telebot.types import Message, BotCommand, BotCommandScope, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

from missedbot import bot
from missedbot.handlers.menu import admin_menu_keyboard, student_menu_keyboard
from database import crud
from telebot.asyncio_handler_backends import StatesGroup, State
from missedbot.handlers.create_team import handle_create_team, callback_choose_discipline, TeamStates
from missedbot.handlers.join_team import handle_join_team, callback_join_team, callback_join_team_select
from missedbot.handlers.menu import student_menu_keyboard
from missedbot.handlers.handle_my_teams import handle_my_teams, callback_manage_team, callback_next_team
# Словарь для хранения информации о пользователях
user_data = {}

@bot.message_handler(commands=["start"])
async def handle_start(message: Message):
    user_id = message.from_user.id
    if crud.is_admin(user_id):
        await bot.set_my_commands(
            commands=[
                BotCommand('addstudent', 'Добавить студента'),
                BotCommand('adddiscipline', 'Добавить дисциплину'),
                BotCommand('discipline2group', 'Назначить дисциплину группе'),
                BotCommand('addgroup', 'Добавить группу'),
                BotCommand('fullreport', 'Полный отчет'),
                BotCommand('shortreport', 'Краткий отчет'),
                BotCommand('interreport', 'Интерактивный отчет'),
                BotCommand('presencecheck', 'Проверка присутствия'),
                BotCommand('delstudent', 'Удалить студента'),
            ],
            language_code='ru',
            scope=BotCommandScope(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
            )
        )
        await bot.send_message(
            message.chat.id,
            "<b>Здравствуйте, хозяин!</b>",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=admin_menu_keyboard(),
        )
    else:
        student = crud.get_student_by_telegram_id(user_id)
        if student:
            await bot.send_message(
                message.chat.id,
                f"Вы уже зарегистрированы как {student.full_name} из группы {crud.get_group(student.group_id).name}.",
                reply_markup=student_menu_keyboard()
            )
        else:
            await bot.send_message(
                message.chat.id,
                "<b>Приветствую тебя!</b>\nПожалуйста, введи номер своей группы:",
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=ForceReply(selective=True)
            )
            user_data[user_id] = {}

@bot.message_handler(func=lambda message: message.reply_to_message and "Пожалуйста, введи номер своей группы" in message.reply_to_message.text)
async def handle_group_number(message: Message):
    user_id = message.from_user.id
    group_name = message.text
    group = crud.get_group_by_name(group_name)

    if group:
        user_data[user_id]['group_id'] = group.id
        user_data[user_id]['group_name'] = group.name
        await bot.send_message(
            message.chat.id,
            "Спасибо! Теперь введи свои ФИО:",
            reply_markup=ForceReply(selective=True)
        )
    else:
        await bot.send_message(
            message.chat.id,
            "Группа не найдена. Пожалуйста, попробуйте снова.",
            reply_markup=ForceReply(selective=True)
        )

@bot.message_handler(func=lambda message: message.reply_to_message and "Теперь введи свои ФИО" in message.reply_to_message.text)
async def handle_full_name(message: Message):
    user_id = message.from_user.id
    full_name = message.text
    group_id = user_data[user_id]['group_id']
    student = crud.get_student_by_name_and_group(full_name, group_id)

    if student:
        if student.is_registered:
            await bot.send_message(
                message.chat.id,
                "Студент уже зарегистрирован.",
            )
        else:
            crud.link_telegram_account(student.id, user_id)
            crud.set_student_registered(student.id)
            user_data[user_id]['full_name'] = student.full_name
            await bot.send_message(
                message.chat.id,
                f"Спасибо! Ты зарегистрирован как {student.full_name} из группы {user_data[user_id]['group_name']}.",
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=student_menu_keyboard()
            )
    else:
        await bot.send_message(
            message.chat.id,
            "Студент не найден в указанной группе. Пожалуйста, попробуйте снова.",
            reply_markup=ForceReply(selective=True)
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("create_team_"))
async def callback_create_team(call):
    discipline_id = int(call.data.split("_")[2])
    user_id = call.from_user.id
    student = crud.get_student_by_telegram_id(user_id)

    if not student:
        await bot.send_message(call.message.chat.id, "Студент не найден.")
        return
    
    team_name = f"Team_{student.group_id}_{discipline_id}"
    team = crud.create_team(team_name, discipline_id, student.group_id, student.id)
    crud.join_team(team.id, student.id)

    await bot.send_message(call.message.chat.id, f"Команда {team_name} создана. Вы являетесь создателем команды.", reply_markup=student_menu_keyboard())

# Обработчик управления командой

@bot.message_handler(func=lambda message: message.text == "Команда")
async def handle_team_management(message: Message):
    user_id = message.from_user.id
    student = crud.get_student_by_telegram_id(user_id)
    if not student.team_id:
        await bot.send_message(message.chat.id, "Вы не состоите в команде.")
        return

    team = crud.get_team_by_id(student.team_id)
    markup = InlineKeyboardMarkup()
    if team.creator_id == student.id:
        markup.add(InlineKeyboardButton("Закрыть набор", callback_data=f"close_team_{team.id}"))
        markup.add(InlineKeyboardButton("Загрузить отчет", callback_data=f"upload_report_{team.id}"))
    markup.add(InlineKeyboardButton("Состав группы", callback_data=f"team_members_{team.id}"))

    await bot.send_message(message.chat.id, "Управление командой:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("close_team_"))
async def callback_close_team(call):
    team_id = int(call.data.split("_")[2])
    crud.close_team(team_id)
    await bot.send_message(call.message.chat.id, "Набор в команду закрыт.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("team_members_"))
async def callback_team_members(call):
    team_id = int(call.data.split("_")[2])
    members = crud.get_team_members(team_id)
    member_list = "\n".join([member.full_name for member in members])
    await bot.send_message(call.message.chat.id, f"Состав команды:\n{member_list}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("upload_report_"))
async def callback_upload_report(call):
    team_id = int(call.data.split("_")[2])
    # Реализация загрузки отчета
    await bot.send_message(call.message.chat.id, "Функция загрузки отчета еще не реализована.")
    
@bot.callback_query_handler(func=lambda call: call.data.startswith("create_team_"))
async def callback_create_team(call):
    discipline_id = int(call.data.split("_")[2])
    user_id = call.from_user.id
    student = crud.get_student_by_telegram_id(user_id)

    if not student:
        await bot.send_message(call.message.chat.id, "Студент не найден.")
        return
    
    team_name = f"Team_{student.group_id}_{discipline_id}"
    team = crud.create_team(team_name, discipline_id, student.group_id, student.id)
    crud.join_team(team.id, student.id)

    await bot.send_message(call.message.chat.id, f"Команда {team_name} создана. Вы являетесь создателем команды.", reply_markup=student_menu_keyboard())
    print(f"Команда {team_name} успешно создана и студент {student.full_name} присоединился.") 

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
    print(f"Студент {student.full_name} успешно присоединился к команде {team.name}.")  






