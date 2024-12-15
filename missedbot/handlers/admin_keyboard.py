from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from enum import Enum, auto
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton

class AdminException(Exception):
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
    SHOW_REPORTS = auto()

__admin_commands = {
    Command.DOWNLOAD_SHORT_REPORT: "Краткий отчет",
    Command.DOWNLOAD_FULL_REPORT: "Полный отчет",
    Command.INTERACTIVE_REPORT: "Интерактивный отчет",
    Command.PRESENCE_CHECK: "Проверка присутствия",
    Command.SEE_GROUP: "Список группы",
    Command.SHOW_REPORTS: "Отчёты студентов",
}

def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Генерирует объект ReplyKeyboardMarkup, содержащий опции меню для администратора.
    :return: Объект ReplyKeyboardMarkup, содержащий опции меню администратора.
    :rtype: ReplyKeyboardMarkup
    """
    markup = ReplyKeyboardMarkup(row_width=3)
    markup.add(
        KeyboardButton(
            __admin_commands[Command.PRESENCE_CHECK],
        ),
        KeyboardButton(
            __admin_commands[Command.SEE_GROUP],
        ),
    )
    markup.add(
        KeyboardButton(
            __admin_commands[Command.DOWNLOAD_SHORT_REPORT],
        ),
        KeyboardButton(
            __admin_commands[Command.DOWNLOAD_FULL_REPORT],
        ),
    )
    markup.add(
        KeyboardButton(
            __admin_commands[Command.INTERACTIVE_REPORT],
        ),
        KeyboardButton(
            __admin_commands[Command.SHOW_REPORTS],
        ),
    )
    return markup