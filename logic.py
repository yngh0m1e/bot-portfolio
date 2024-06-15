import sqlite3
from config import DATABASE, TOKEN
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup

# Data for inserting into tables
skills = [(_,) for _ in (['Python', 'SQL', 'API', 'Telegram'])]
statuses = [(_,) for _ in (['На этапе проектирования', 'В процессе разработки', 'Разработан. Готов к использованию.', 'Обновлен', 'Завершен. Не поддерживается'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            photo TEXT,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''') 
            conn.execute('''CREATE TABLE IF NOT EXISTS skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id),
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')
            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    
    def __select_data(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
        
    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO skills (skill_name) values(?)'
        data = skills
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)

    def insert_project(self, data):
        sql = 'INSERT INTO projects (user_id, project_name, description, url, status_id, photo) VALUES (?, ?, ?, ?, ?, ?)'
        self.__executemany(sql, data)

    def insert_or_update_project(self, user_id, project_name, description, url, status_id, photo):
        project_id = self.__select_data('SELECT project_id FROM projects WHERE user_id = ? AND project_name = ?', (user_id, project_name))
        if project_id:
            self.update_projects('url', (url, project_id[0][0]))
            self.update_projects('photo', (photo, project_id[0][0]))
        else:
            self.insert_project([(user_id, project_name, description, url, status_id, photo)])

    def insert_skill(self, user_id, project_name, skill):
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        project_id = self.__select_data(sql, (project_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skills VALUES(?, ?)'
        self.__executemany(sql, data)

    def get_statuses(self):
        sql = 'SELECT * FROM status'
        return self.__select_data(sql)

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_projects(self, user_id):
        sql = 'SELECT * FROM projects WHERE user_id = ?'
        return self.__select_data(sql, data=(user_id,))
        
    def get_project_id(self, project_name, user_id):
        return self.__select_data(sql='SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?', data=(project_name, user_id,))[0][0]
        
    def get_skills(self):
        return self.__select_data(sql='SELECT * FROM skills')
    
    def get_project_skills(self, project_name):
        res = self.__select_data(sql='''SELECT skill_name FROM projects 
JOIN project_skills ON projects.project_id = project_skills.project_id 
JOIN skills ON skills.skill_id = project_skills.skill_id 
WHERE project_name = ?''', data=(project_name,))
        return ', '.join([x[0] for x in res])
    
    def get_project_info(self, user_id, project_name):
        sql = """
SELECT project_name, description, url, status_name, photo FROM projects 
JOIN status ON
status.status_id = projects.status_id
WHERE project_name=? AND user_id=?
"""
        return self.__select_data(sql=sql, data=(project_name, user_id))

    def update_projects(self, param, data):
        sql = f'UPDATE projects SET {param} = ? WHERE project_id = ?'
        self.__executemany(sql, [data]) 

    def delete_project(self, user_id, project_id):
        sql = 'DELETE FROM projects WHERE user_id = ? AND project_id = ?'
        self.__executemany(sql, [(user_id, project_id)])
    
    def delete_skill(self, project_id, skill_id):
        sql = 'DELETE FROM project_skills WHERE skill_id = ? AND project_id = ?'
        self.__executemany(sql, [(skill_id, project_id)])

    def add_photo_column(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(projects)")
            columns = [info[1] for info in cur.fetchall()]
            if 'photo' not in columns:
                conn.execute('ALTER TABLE projects ADD COLUMN photo TEXT')
                conn.commit()

def start(update, context):
    keyboard = [['📄 Info', '❓ Help']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    welcome_message = (
        "👋 *Welcome to the Bot!* 👋\n\n"
        "Choose a command from the menu below to get started."
    )
    update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

def info(update, context):
    info_message = (
        "📜 *Bot Commands* 📜\n\n"
        "/start - Start the bot and display the main menu\n"
        "/info - Show information about the bot commands\n"
        "/help - Get help on how to use the bot\n"
    )
    update.message.reply_text(info_message, parse_mode='Markdown')

def help_command(update, context):
    help_message = (
        "❓ *Help* ❓\n\n"
        "To use this bot, you can start by using the /start command to see the main menu. "
        "From there, you can choose other commands to learn more or get assistance."
    )
    update.message.reply_text(help_message, parse_mode='Markdown')

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

# Добавление столбца для описания проекта
def add_description_column(self):
    conn = sqlite3.connect(self.database)
    with conn:
        conn.execute('ALTER TABLE projects ADD COLUMN IF NOT EXISTS description TEXT')
        conn.commit()

# Добавление столбца для названия файла фото проекта
def add_photo_filename_column(self):
    conn = sqlite3.connect(self.database)
    with conn:
        conn.execute('ALTER TABLE projects ADD COLUMN IF NOT EXISTS photo_filename TEXT')
        conn.commit()

# Вставка или обновление статуса проекта
def insert_or_update_status(self, project_id, status_id):
    sql = 'UPDATE projects SET status_id = ? WHERE project_id = ?'
    self.__executemany(sql, [(status_id, project_id)])

# Вставка или обновление навыка проекта
def insert_or_update_skill(self, project_id, skill_id):
    sql = 'INSERT OR IGNORE INTO project_skills VALUES (?, ?)'
    self.__executemany(sql, [(project_id, skill_id)])
