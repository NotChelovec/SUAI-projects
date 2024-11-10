import os
import sqlite3
import telebot
from telebot import types 

BOT_TOKEN = os.environ.get('7562465469:AAGqnwtk7odixnropr_3jXEcKZfzEyEV2oA')
bot = telebot.TeleBot('7562465469:AAGqnwtk7odixnropr_3jXEcKZfzEyEV2oA')

#Базы данных
conn = sqlite3.connect('messages.db')
cursor = conn.cursor()
cursor.execute("")

# Никнейм преподавателя
TEACHERS = ["todaysha"]

@bot.message_handler(commands=['start'])
def start_command(message):
  keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
  if message.from_user.username in TEACHERS:
      # Интерфейс для преподавателя
      project_button = types.KeyboardButton("Управление проектами")
      student_list_button = types.KeyboardButton("Список студентов")
      reports_button = types.KeyboardButton("Отчеты")
      help_button = types.KeyboardButton("Команды")
      keyboard.add(project_button, student_list_button, reports_button, help_button)
      bot.send_message(message.chat.id, "Добро пожаловать, преподаватель! 🎓", reply_markup=keyboard)
  else:
      # Обычный интерфейс для пользователей
      menu_button = types.KeyboardButton("Меню")
      help_button = types.KeyboardButton("Команды")
      projects_button = types.KeyboardButton("Проекты")
      contacts_button = types.KeyboardButton("Контакты")
      keyboard.add(menu_button, help_button, projects_button, contacts_button)
      bot.send_message(message.chat.id, "Привет, вы зашли в бот для проектов! 👋", reply_markup=keyboard)

@bot.message_handler(commands=['main'])
def start_command(message):
  keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
  if message.from_user.username in TEACHERS:
      # Интерфейс для преподавателя
      project_button = types.KeyboardButton("Управление проектами")
      student_list_button = types.KeyboardButton("Список студентов")
      reports_button = types.KeyboardButton("Отчеты")
      help_button = types.KeyboardButton("Команды")
      keyboard.add(project_button, student_list_button, reports_button, help_button)
      bot.send_message(message.chat.id, "Добро пожаловать, преподаватель! 🎓", reply_markup=keyboard)
  else:
      # Обычный интерфейс для пользователей
      menu_button = types.KeyboardButton("Меню")
      help_button = types.KeyboardButton("Команды")
      projects_button = types.KeyboardButton("Проекты")
      contacts_button = types.KeyboardButton("Контакты")
      keyboard.add(menu_button, help_button, projects_button, contacts_button)
      bot.send_message(message.chat.id, "Привет, вы зашли в бот для проектов! 👋", reply_markup=keyboard)
      
@bot.message_handler(commands=['about'])
def about_command(message):
    bot.reply_to(message, "Я бот для проектов, помогающий студентам и преподавателям.\n\nSUAI_project_bot может:\n\n🗃️ - Показывать список проектов которвые вы создали\n👨‍💼  - Предоставлять информацию о преподавателях\n💬 - Организовывать наиболее удобное взаимодействие")

@bot.message_handler(commands=['info'])
def about_command(message):
    bot.reply_to(message, "У меня есть следующие команды:\n/start\n/menu\n/help\n/about")
    
@bot.message_handler(func=lambda message: message.text == "Управление проетами")
def manage_projects(message):
  if message.from_user.username in TEACHERS:
      bot.reply_to(message, "Здесь вы можете управлять проектами.")
  else:
      bot.reply_to(message, "Эта функция доступна только преподавателю.")

@bot.message_handler(func=lambda message: message.text == "Список студентов")
def student_list(message):
  if message.from_user.username in TEACHERS:
      bot.reply_to(message, "Список студентов.")
  else:
      bot.reply_to(message, "Эта функция доступна только преподавателю.")

@bot.message_handler(func=lambda message: message.text == "Отчеты")
def reports(message):
  if message.from_user.username in TEACHERS:
      bot.reply_to(message, "Просмотр отчетов.")
  else:
      bot.reply_to(message, "Эта функция доступна только преподавателю.")

@bot.message_handler(func=lambda message: message.text == "Меню")
def menu_command(message):
  bot.reply_to(message, "Вы находитесь в меню. Как я могу помочь?")

@bot.message_handler(func=lambda message: message.text == "Редактор команды")
def edit_command(message):
  bot.reply_to(message, "Необходимо добавить базы данных")

@bot.message_handler(func=lambda message: message.text == "Создать проект")
def add_project(message):
  bot.reply_to(message, "Необходимо добавить базы данных")

@bot.message_handler(func=lambda message: message.text == "Перейти в проект")
def edit_project(message):
  bot.reply_to(message, "Необходимо добавить базы данных")

@bot.message_handler(func=lambda message: message.text == "Проекты")
def projects_command(message):
  if message.from_user.username not in TEACHERS:
    keybord = keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_add_command = types.KeyboardButton("Редактор команды")
    button_add_project = types.KeyboardButton("Создать проект")
    button_edit_project = types.KeyboardButton("Перейти в проект")
    keybord.add(button_add_command, button_add_project, button_edit_project)
    bot.reply_to(message, "В разделе 'проекты' вам доступны следующее возможности:\n\n📝 - Создать проект\n👥 - Редактор Команды\n📋 - Перейти в проект", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Контакты")
def contacts_command(message):
  bot.send_photo(message.chat.id, 'https://pro.guap.ru/avatars/9/8544.jpg', caption= "Преподаватель: Чернышев Станислав Андреевич:\nПочта: madteacher@bk.ru\nТелеграм: @MADComrade")

@bot.message_handler(func=lambda message: message.text == "Команды")
def help_command(message):
  bot.reply_to(message, "У меня есть следующие команды:\n/start\n/menu\n/info\n/about")


bot.polling()

