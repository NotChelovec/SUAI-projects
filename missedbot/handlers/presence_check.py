from telebot.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from database import crud
from missedbot import bot


_student_missed: list[int] = []
PAGINATOR = 5
__report_prefix = [
    "presenceDis_",
    "presenceGroup_",
    "studClick_",
]


def __is_prefix_callback(data: str) -> bool:
    """
    Проверяет, является ли данная строка префиксом любого
    из элементов списка `__report_prefix`.
    """
    for it in __report_prefix:
        if it in data:
            return True
    return False


@bot.message_handler(
    is_admin=True,
    commands=["presencecheck"],
)
async def handle_presence_check(message: Message):
    await presence_check(message)


@bot.message_handler(
    is_admin=False,
    commands=["presencecheck"],
)
async def handle_no_presence_check(message: Message):
    await bot.send_message(message.chat.id, "Ты кто? Оо")


async def presence_check(message: Message):
    """
    Отправляет сообщение с перечнем дисциплин и их ID в
    виде кнопок типа Inline. Пользователь может выбрать дисциплину,
    нажав на соответствующую кнопку. Выбранный ID дисциплины передается
    в виде callback-данных в функцию, указанную в поле
    "callback_data" кнопки.
    """
    disciplines = crud.get_disciplines()
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        *[
            InlineKeyboardButton(
                it.name,
                callback_data=f"presenceDis_{it.id}",
            )
            for it in disciplines
        ]
    )
    await bot.send_message(
        message.chat.id,
        "Выберете дисциплину:",
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: __is_prefix_callback(call.data),
)
async def callback_presence_check(call):
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "presenceDis":
            # Выводим список групп у которых преподается
            # выбранная дисциплина
            discipline_id = int(call.data.split("_")[1])
            groups = crud.get_assigned_group(discipline_id)
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(
                *[
                    InlineKeyboardButton(
                        it.name,
                        callback_data=f"presenceGroup_0_{discipline_id}_{it.id}",
                    )
                    for it in groups
                ]
            )
            _student_missed.clear()
            await bot.edit_message_text(
                "Выберите группу:",
                call.message.chat.id,
                call.message.id,
                reply_markup=markup,
            )
        case "presenceGroup" | "studClick":
            # Выводим список студентов группы
            # если был выбран конкретный студент,
            # то он добавляется в список отсутствующий и помечается
            # ❌ при повторном отображении ботом, если он уже был в списке,
            # то он удаляется из него
            paginator = int(call.data.split("_")[1])
            discipline_id = int(call.data.split("_")[2])
            group_id = int(call.data.split("_")[3])
            if type_callback == "studClick":
                student_id = int(call.data.split("_")[4])
                if student_id in _student_missed:
                    _student_missed.remove(student_id)
                else:
                    _student_missed.append(student_id)
            await student_check(
                call,
                paginator,
                discipline_id,
                group_id,
            )
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных",
                call.message.chat.id,
                call.message.id,
            )


async def student_check(
    call,
    paginator: int,
    discipline_id: int,
    group_id: int,
) -> None:
    """
    Получает список студентов для заданного group_id,
    пагинирует их и выводит с кнопками выбора пропущенных студентов.

    :param call: Callback-запрос от пользователя.
    :param paginator: Целочисленное значение, представляющее номер страницы пагинации.
    :param discipline_id: Целочисленное значение, представляющее ID дисциплины.
    :param group_id: Целочисленное значение, представляющее ID группы.
    :return: None
    """
    students = crud.get_students(group_id)

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        *[
            InlineKeyboardButton(
                f"✔️{it.full_name}"
                if it.id not in _student_missed
                else f"❌{it.full_name}",
                callback_data=f"studClick_{paginator}_{discipline_id}_{group_id}_{it.id}",
            )
            for it in students[PAGINATOR * paginator : PAGINATOR * (paginator + 1)]
        ]
    )
    if paginator == 0:
        markup.add(
            InlineKeyboardButton(
                "➡",
                callback_data=f"presenceGroup_{paginator + 1}_{discipline_id}_{group_id}",
            )
        )
    elif len(students) > PAGINATOR * (paginator + 1):
        markup.add(
            InlineKeyboardButton(
                "⬅",
                callback_data=f"presenceGroup_{paginator - 1}_{discipline_id}_{group_id}",
            ),
            InlineKeyboardButton(
                "➡",
                callback_data=f"presenceGroup_{paginator + 1}_{discipline_id}_{group_id}",
            ),
            row_width=2,
        )
    else:
        markup.add(
            InlineKeyboardButton(
                "⬅",
                callback_data=f"presenceGroup_{paginator - 1}_{discipline_id}_{group_id}",
            )
        )
    markup.add(
        InlineKeyboardButton(
            "Аудитория полна людей", callback_data=f"allPresent_{discipline_id}_{group_id}"
        ),
        InlineKeyboardButton(
            "Аудитория пуста", callback_data=f"allMissed_{discipline_id}_{group_id}"
        ),
        row_width=2,
    )
    markup.add(
        InlineKeyboardButton(
            "Зафиксировать помещаемость", callback_data=f"apply_{discipline_id}_{group_id}"
        ),
        row_width=1,
    )
    await bot.edit_message_text(
        "Выберите отсутствующего студента:",
        call.message.chat.id,
        call.message.id,
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: ("allPresent_" in call.data or "allMissed_" in call.data),
)
async def callback_all_missed_present(call):
    """
    Когда все студенты присутствуют или отсутствуют.
    """
    event = call.data.split("_")[0]
    discipline_id = int(call.data.split("_")[1])
    group_id = int(call.data.split("_")[2])
    _student_missed.clear()
    text = ""
    is_missed = False
    match event:
        case "allPresent":
            text = "Все студенты присутствуют на занятии!"
        case "allMissed":
            is_missed = True
            text = "На паре нет ни одного студента!"

    crud.set_all_missed_students(
        group_id,
        discipline_id,
        is_missed,
    )
    await bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.id,
    )


@bot.callback_query_handler(func=lambda call: "apply_" in call.data)
async def callback_all_present(call):
    """
    Зафиксировать в БД выбранных отсутствующих и
    присутствующих студентов
    """
    discipline_id = int(call.data.split("_")[1])
    group_id = int(call.data.split("_")[2])

    crud.set_missed_students(
        _student_missed,
        group_id,
        discipline_id,
    )
    await bot.edit_message_text(
        "Посещаемость зафиксированна.",
        call.message.chat.id,
        call.message.id,
    )