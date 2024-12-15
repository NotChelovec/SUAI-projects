from enum import Enum, auto

from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton

from missedbot import bot
from missedbot.handlers.download_report import start_download_report
from missedbot.handlers.interactive_report import start_interactive_report
from missedbot.handlers.presence_check import presence_check
from missedbot.handlers.see_group import see_student
from missedbot.handlers.handle_my_teams import handle_my_teams
from missedbot.handlers.create_team import handle_create_team
from missedbot.handlers.join_team import handle_join_team
from missedbot.handlers.student_keyboard import student_menu_keyboard, __student_commands
from missedbot.handlers.admin_keyboard import admin_menu_keyboard, __admin_commands, Command
from missedbot.handlers.admin_view import handle_view_reports

class AdminException(Exception):
    ...

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
    SHOW_REPORTS = auto()

__admin_commands = {
    Command.DOWNLOAD_SHORT_REPORT: "Краткий отчет",
    Command.DOWNLOAD_FULL_REPORT: "Полный отчет",
    Command.INTERACTIVE_REPORT: "Интерактивный отчет",
    Command.PRESENCE_CHECK: "Проверка присутствия",
    Command.SEE_GROUP: "Список группы",
    Command.SHOW_REPORTS: "Отчёты студентов",
}

__student_commands = {
    Command.SEE_GROUP: "Список группы",
    Command.SEND_REPORT: "Отправить отчёт",
    Command.SHOW_GROUP: "Состав группы",
    Command.CREATE_TEAM: "Создать команду",
    Command.JOIN_TEAM: "Присоединиться к группе",
    Command.MANAGE_TEAM: "Мои команды",
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

def is_admin_command(command: str) -> bool:
    """
    Проверяет, является ли указанная команда командой администратора, ища ее в словаре __admin_commands.
    :param command: Строка, представляющая проверяемую команду.
    :type command: str
    :return: Булево значение, указывающее, является ли команда командой администратора.
    :rtype: bool
    """
    for key, value in __admin_commands.items():
        if value == command:
            return True
    return False

def is_student_command(command: str) -> bool:
    """
    Проверяет, является ли указанная команда командой студента, ища ее в словаре __student_commands.
    :param command: Строка, представляющая проверяемую команду.
    :type command: str
    :return: Булево значение, указывающее, является ли команда командой студента.
    :rtype: bool
    """
    for key, value in __student_commands.items():
        if value == command:
            return True
    return False

def get_current_admin_command(command: str) -> Command:
    """
    Возвращает ключ команды, если она есть в словаре __admin_commands, в противном случае вызывается исключение AdminException.
    Args:
        command (str): Команда для поиска в словаре __admin_commands.
    Returns:
        Ключ команды, если она есть в словаре __admin_commands.
    Raises:
        AdminException: Если команда не найдена в словаре __admin_commands.
    """
    for key, value in __admin_commands.items():
        if value == command:
            return key
    raise AdminException("Неизвестная команда")

def get_current_student_command(command: str) -> Command:
    """
    Возвращает ключ команды, если она есть в словаре __student_commands, в противном случае вызывается исключение StudentException.
    Args:
        command (str): Команда для поиска в словаре __student_commands.
    Returns:
        Ключ команды, если она есть в словаре __student_commands.
    Raises:
        StudentException: Если команда не найдена в словаре __student_commands.
    """
    for key, value in __student_commands.items():
        if value == command:
            return key
    raise StudentException("Неизвестная команда")

@bot.message_handler(
    is_admin=True,
    func=lambda message: is_admin_command(message.text),
)
async def handle_admin_commands(message: Message):
    """
    Обрабатывает команды администратора, отправленные в виде сообщений боту. Принимает объект сообщения, и в зависимости
    от содержащейся в нем команды, вызывает другие функции для выполнения конкретных действий.
    Функция вызывается только если отправитель сообщения является администратором и текст сообщения распознан
    как команда администратора. Распознаваемые команды: PRESENCE_CHECK, DOWNLOAD_FULL_REPORT, DOWNLOAD_SHORT_REPORT,
    INTERACTIVE_REPORT и SEE_GROUP. Для каждой команды вызывается определенная функция для выполнения соответствующего действия.
    :param message: Объект сообщения, содержащий текст команды и другую информацию.
    :type message: Message
    :return: None
    """
    command = get_current_admin_command(message.text)
    match command:
        case Command.PRESENCE_CHECK:
            await presence_check(message)
        case Command.DOWNLOAD_FULL_REPORT:
            await start_download_report(message, "fullReport")
        case Command.DOWNLOAD_SHORT_REPORT:
            await start_download_report(message, "shortReport")
        case Command.INTERACTIVE_REPORT:
            await start_interactive_report(message)
        case Command.SEE_GROUP:
            await see_student(message)
        case Command.SHOW_REPORTS(message):
            await handle_view_reports(message)

@bot.message_handler(
    is_admin=False,
    func=lambda message: is_student_command(message.text),
)
async def handle_student_commands(message: Message):
    """
    Обрабатывает команды студента, отправленные в виде сообщений боту. Принимает объект сообщения, и в зависимости
    от содержащейся в нем команды, вызывает другие функции для выполнения конкретных действий.
    Функция вызывается только если отправитель сообщения является студентом и текст сообщения распознан
    как команда студента. Распознаваемые команды: SEE_GROUP, SEND_REPORT и SHOW_GROUP. Для каждой команды
    вызывается определенная функция для выполнения соответствующего действия.
    :param message: Объект сообщения, содержащий текст команды и другую информацию.
    :type message: Message
    :return: None
    """
    command = get_current_student_command(message.text)
    match command:
        case Command.SEE_GROUP:
            await see_student(message)
        case Command.SEND_REPORT:
            await bot.send_message(message.chat.id, "1")
        case Command.SHOW_GROUP:
            await bot.send_message(message.chat.id, "1")
        case Command.MANAGE_TEAM:
            await handle_my_teams(message)
        case Command.CREATE_TEAM:
            await handle_create_team(message)
        case Command.JOIN_TEAM:
            await handle_join_team(message)
