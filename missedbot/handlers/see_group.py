from telebot.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from database import crud
from missedbot import bot



@bot.message_handler(
    commands=["presencecheck"],
)
async def handle_presence_check(message: Message):
    await see_student(message)


async def see_student(message: Message):
    """
    Отправляет сообщение с перечнем групп и их ID в
    виде кнопок типа Inline. Пользователь может выбрать группу,
    нажав на соответствующую кнопку. Выбранный ID группы передается
    в виде callback-данных в функцию, указанную в поле
    "callback_data" кнопки.
    """
    groups = crud.get_groups()
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        *[
            InlineKeyboardButton(
                group.name,
                callback_data=f"group_{group.id}",
            )
            for group in groups
        ]
    )
    await bot.send_message(
        message.chat.id,
        "Выберите группу:",
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("group_"),
)
async def callback_group_selection(call):
    """
    Обработчик выбора группы. После выбора группы
    выводится список студентов этой группы.
    """
    group_id = int(call.data.split("_")[1])
    await student_list(call.message, group_id)


async def student_list(message: Message, group_id: int):
    """
    Отправляет сообщение с перечнем студентов выбранной группы в виде блоков.
    """
    students = crud.get_students(group_id)
    if not students:
        text = "Список студентов пуст."
        await bot.send_message(
            message.chat.id,
            text,
        )
    else:
        # Создание разметки с кнопками для студентов
        markup = InlineKeyboardMarkup()
        for student in students:
            markup.add(InlineKeyboardButton(student.full_name, callback_data=f"student_{student.id}"))
        
        await bot.send_message(
            message.chat.id,
            "Список студентов:",
            reply_markup=markup,
        )
