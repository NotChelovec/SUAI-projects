from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from enum import Enum, auto
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton


class StudentException(Exception):
    ...

class Command(Enum):
    DOWNLOAD_SHORT_REPORT = auto()
    DOWNLOAD_FULL_REPORT = auto()
    INTERACTIVE_REPORT = auto()
    PRESENCE_CHECK = auto()
    SEE_GROUP = auto()
    SEND_REPORT = auto()
    SHOW_GROUP = auto()
    CREATE_TEAM = auto()
    JOIN_TEAM = auto()
    MANAGE_TEAM = auto()

__student_commands = {
    Command.SEE_GROUP: "Список группы",
    Command.SEND_REPORT: "Отправить отчёт",
    Command.SHOW_GROUP: "Состав группы",
    Command.CREATE_TEAM: "Создать команду",
    Command.JOIN_TEAM: "Присоединиться к группе",
    Command.MANAGE_TEAM: "Мои команды",
}
    
def student_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Генерирует объект ReplyKeyboardMarkup, содержащий опции меню для студента.
    :return: Объект ReplyKeyboardMarkup, содержащий опции меню студента.
    :rtype: ReplyKeyboardMarkup
    """
    markup = ReplyKeyboardMarkup(row_width=3)
    markup.add(
        KeyboardButton(
            __student_commands[Command.SEE_GROUP],
        ),
    )
    markup.add(
        KeyboardButton(
            __student_commands[Command.CREATE_TEAM],
        ),
        KeyboardButton(
            __student_commands[Command.JOIN_TEAM],
        ),
    )
    markup.add(
        KeyboardButton(__student_commands[Command.MANAGE_TEAM]),
    )
    return markup
