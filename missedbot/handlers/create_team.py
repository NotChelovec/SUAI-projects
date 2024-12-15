from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.asyncio_handler_backends import StatesGroup, State
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from missedbot.handlers.student_keyboard import student_menu_keyboard
from missedbot import bot
from database import crud

class TeamStates(StatesGroup):
    CHOOSE_DISCIPLINE = State()
    INPUT_TEAM_NAME = State()

@bot.message_handler(func=lambda message: message.text == "Создать команду")
async def handle_create_team(message: Message):
    user_id = message.from_user.id
    student = crud.get_student_by_telegram_id(user_id)
    disciplines = crud.get_disciplines()
    markup = InlineKeyboardMarkup()
    for discipline in disciplines:
        markup.add(InlineKeyboardButton(discipline.name, callback_data=f"choose_discipline_{discipline.id}"))

    await bot.send_message(message.chat.id, "Выберите дисциплину:", reply_markup=markup)
    await bot.set_state(user_id, TeamStates.CHOOSE_DISCIPLINE, message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("choose_discipline_"))
async def callback_choose_discipline(call):
    discipline_id = int(call.data.split("_")[2])
    user_id = call.from_user.id

    student = crud.get_student_by_telegram_id(user_id)
    if not student:
        await bot.send_message(call.message.chat.id, "Студент не найден.")
        return
    
    if crud.user_has_team_in_discipline(student.id, discipline_id):
        await bot.send_message(call.message.chat.id, "Вы уже создали команду в этой дисциплине.")
        return

    async with bot.retrieve_data(user_id, call.message.chat.id) as data:
        data['discipline_id'] = discipline_id

    await bot.set_state(user_id, TeamStates.INPUT_TEAM_NAME, call.message.chat.id)
    await bot.send_message(call.message.chat.id, "Введите название команды:")

@bot.message_handler(state=TeamStates.INPUT_TEAM_NAME)
async def handle_team_name(message: Message):
    team_name = message.text
    user_id = message.from_user.id

    async with bot.retrieve_data(user_id, message.chat.id) as data:
        discipline_id = data['discipline_id']
        student = crud.get_student_by_telegram_id(user_id)
        if not student:
            await bot.send_message(message.chat.id, "Студент не найден.")
            return

        team_number = crud.get_next_team_number(discipline_id, student.group_id)
        full_team_name = f"Команда {team_number} {team_name}"

        try:
            team = crud.create_team(full_team_name, discipline_id, student.group_id, student.id)
            crud.join_team(team.id, student)
        except Exception as e:
            await bot.send_message(message.chat.id, f"Произошла ошибка при создании или присоединении к команде: {e}")
            return

    await bot.send_message(message.chat.id, f"Команда {full_team_name} создана. Вы являетесь создателем команды.", reply_markup=student_menu_keyboard())
    await bot.delete_state(user_id, message.chat.id)
