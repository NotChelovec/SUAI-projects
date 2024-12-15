from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from missedbot.handlers.student_keyboard import student_menu_keyboard
from missedbot import bot
from database import crud

@bot.message_handler(func=lambda message: message.text == "Мои команды")
async def handle_my_teams(message: Message):
    user_id = message.from_user.id
    student = crud.get_student_by_telegram_id(user_id)
    if not student:
        await bot.send_message(message.chat.id, "Студент не найден.")
        return

    teams = crud.get_teams_created_by_user(student.id)
    if not teams:
        await bot.send_message(message.chat.id, "Вы не создали ни одной команды.")
        return

    # Сохраняем команды пользователя в context user data для переключения между ними
    async with bot.retrieve_data(user_id, message.chat.id) as data:
        data['teams'] = teams
        data['current_team_index'] = 0

    await show_team_info(message, teams, 0)

@bot.callback_query_handler(func=lambda call: call.data == "next_team")
async def callback_next_team(call):
    user_id = call.from_user.id
    try:
        async with bot.retrieve_data(user_id, call.message.chat.id) as data:
            teams = data['teams']
            current_team_index = data['current_team_index']
            
            next_team_index = (current_team_index + 1) % len(teams)
            data['current_team_index'] = next_team_index
            
        team_id = data['teams'][next_team_index].id
        team = crud.get_team_by_id(team_id)
        await show_team_info(call.message, [team], 0)
    except Exception as e:
        print(f"Error in next_team callback: {e}")
        await bot.send_message(call.message.chat.id, "Произошла ошибка при переключении команды.")

async def show_team_info(message: Message, teams, index):
    try:
        team = teams[index]
        discipline_name = crud.get_discipline_by_id(team.discipline_id).name
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Далее", callback_data="next_team"))
        markup.add(InlineKeyboardButton("Управление командой", callback_data=f"manage_team_{team.id}"))
        
        await bot.send_message(message.chat.id, f"{discipline_name} - группа {team.name}", reply_markup=markup)
    except Exception as e:
        print(f"Error in show_team_info: {e}")
        await bot.send_message(message.chat.id, "Произошла ошибка при отображении информации о команде.")
    
@bot.callback_query_handler(func=lambda call: call.data.startswith("manage_team_"))
async def callback_manage_team(call):
    try:
        team_id = int(call.data.split("_")[2])
        user_id = call.from_user.id
        team = crud.get_team_by_id(team_id)
        student = crud.get_student_by_telegram_id(user_id)

        if not student or not team:
            await bot.send_message(call.message.chat.id, "Произошла ошибка. Попробуйте снова.")
            return

        markup = InlineKeyboardMarkup()
        if team.creator_id == student.id:
            markup.add(InlineKeyboardButton("Закрыть набор", callback_data=f"close_team_{team.id}"))
            markup.add(InlineKeyboardButton("Загрузить отчет", callback_data=f"upload_report_{team.id}"))
        markup.add(InlineKeyboardButton("Состав группы", callback_data=f"team_members_{team.id}"))

        await bot.send_message(call.message.chat.id, f"Управление командой {team.name}:", reply_markup=markup)
    except Exception as e:
        print(f"Error in manage_team callback: {e}")
        await bot.send_message(call.message.chat.id, "Произошла ошибка при управлении командой.")
