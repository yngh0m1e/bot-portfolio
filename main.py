from logic import DB_Manager
from config import *
from telebot import TeleBot, types
from telebot.types import ReplyKeyboardMarkup

bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove() 
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
        "/help - Get help on how to use the bot\n"
    )
    bot.send_message(message.chat.id, info_message, parse_mode='Markdown')

def help_command(message):
    help_message = (
        "❓ *Help* ❓\n\n"
        "To use this bot, you can start by using the /start command to see the main menu. "
        "From there, you can choose other commands to learn more or get assistance."
    )
    bot.send_message(message.chat.id, help_message, parse_mode='Markdown')

def main():
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()

    manager.add_photo_column()
    
    user_id = 1
    project_name = 'Test Project'
    description = 'Description of Test Project'
    url = 'https://www.google.kz/'
    status_id = 1
    photo = 'https://doctor-veterinar.ru/media/k2/items/cache/675d28c04794e3c683f4419536c4c15f_L.jpg'
    
    manager.insert_or_update_project(user_id, project_name, description, url, status_id, photo)
    
    print(manager.get_projects(user_id))
    print(manager.get_project_info(user_id, project_name))

    manager.insert_skill(user_id, project_name, 'Python')
    print(manager.get_project_skills(project_name))

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        start(message)

    @bot.message_handler(commands=['info'])
    def handle_info(message):
        info(message)

    @bot.message_handler(commands=['help'])
    def handle_help(message):
        help_command(message)

    bot.polling()

if __name__ == '__main__':
    main()