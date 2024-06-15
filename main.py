from logic import DB_Manager
from config import *
from telebot import TeleBot, types
from telebot.types import ReplyKeyboardMarkup
import os

# Initialize bot with token
bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove()

# Handlers for bot commands
def start(message):
    keyboard = [['📄 Info', '❓ Help']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    welcome_message = (
        "👋 *Welcome to the Bot!* 👋\n\n"
        "Choose a command from the menu below to get started.\n"
        "/start 🏁\n"
        "/info 📖\n"
        "/help 🆘"
    )
    bot.send_message(message.chat.id, welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

def info(message):
    info_message = (
        "📜 *Bot Commands* 📜\n\n"
        "/start - Start the bot and display the main menu\n"
        "/info - Show information about the bot commands\n"
        "/help - Get help on how to use the bot\n\n"
        "*Recent Changes:*\n"
        "- Added handler for setting project description\n"
        "- Added ability to upload project photos\n"
        "- Updated logic methods for inserting/updating project statuses and skills\n"
        "- Implemented usage of these methods in the bot logic"
    )
    bot.send_message(message.chat.id, info_message, parse_mode='Markdown')

def help_command(message):
    help_message = (
        "❓ *Help* ❓\n\n"
        "To use this bot, you can start by using the /start command to see the main menu. "
        "From there, you can choose other commands to learn more or get assistance."
    )
    bot.send_message(message.chat.id, help_message, parse_mode='Markdown')
# Добавление хэндлера для описания проекта
@bot.message_handler(func=lambda message: message.text == '📝 Add Description')
def handle_add_description(message):
    bot.send_message(message.chat.id, "Send me the description of your project:")
    bot.register_next_step_handler(message, save_description)

def save_description(message):
    user_id = message.from_user.id
    project_name = message.text
    description = message.text
    manager.insert_or_update_project(user_id, project_name, description, None, None, None)
    bot.send_message(message.chat.id, "Description added successfully.")

# Добавление хэндлера для загрузки фото проекта
@bot.message_handler(content_types=['photo'])
def handle_project_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_info.file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
        # Путь к текущей директории
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # Путь к папке с фотографиями
        photos_dir = os.path.join(current_dir, 'photos')

        # Создать папку, если она не существует
        if not os.path.exists(photos_dir):
            os.makedirs(photos_dir)
    bot.send_message(message.chat.id, "Photo saved successfully.")

# Добавление хэндлеров для управления статусами и навыками проектов
@bot.message_handler(func=lambda message: message.text == '📊 Manage Statuses')
def handle_manage_statuses(message):
    statuses = manager.get_statuses()
    # Отправить список статусов пользователю и позволить выбрать
    # Затем использовать метод insert_or_update_status для обновления статуса проекта

@bot.message_handler(func=lambda message: message.text == '🔧 Manage Skills')
def handle_manage_skills(message):
    skills = manager.get_skills()
    # Отправить список навыков пользователю и позволить выбрать
    # Затем использовать метод insert_or_update_skill для добавления навыка проекта
def main():
    # Initialize the database manager and set up the database
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()

    # Add photo column if not exists
    manager.add_photo_column()
    
    # Test insertion or update
    user_id = 1
    project_name = 'Test Project'
    description = 'Description of Test Project'
    url = 'https://www.google.kz/'
    status_id = 1
    photo = 'https://doctor-veterinar.ru/media/k2/items/cache/675d28c04794e3c683f4419536c4c15f_L.jpg'
    
    manager.insert_or_update_project(user_id, project_name, description, url, status_id, photo)
    
    # Verify insertion or update
    print(manager.get_projects(user_id))
    print(manager.get_project_info(user_id, project_name))

    # Insert skill
    manager.insert_skill(user_id, project_name, 'Python')
    print(manager.get_project_skills(project_name))

    # Add bot handlers
    bot.message_handler(commands=['start'])(start)
    bot.message_handler(commands=['info'])(info)
    bot.message_handler(commands=['help'])(help_command)

    # Start polling for messages
    bot.polling()

if __name__ == '__main__':
    main()
