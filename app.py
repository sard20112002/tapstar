import telebot
from flask import Flask, render_template, request
import sqlite3
import threading
from telebot import types
import json

# === Настройки ===
TOKEN = "7929683034:AAEz07e103Bgx5cPhNdb22xioUl2Qpr-UZ4"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === Инициализация базы данных ===
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  telegram_id INTEGER UNIQUE,
                  name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# === Flask маршруты ===

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.WebAppInfo("https://your-url.app/")  # вставь URL на mini-app
    markup.add(types.KeyboardButton("Открыть MiniApp 🌐", web_app=web_app))
    bot.send_message(message.chat.id, "Привет! Нажми кнопку ниже 👇", reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    try:
        data = json.loads(message.web_app_data.data)
    except:
        data = {}
    action = data.get("action")
    if action == "say_hello":
        msg = data.get("message", "Привет!")
        bot.send_message(message.chat.id, f"Бот говорит: {msg}")
    else:
        bot.send_message(message.chat.id, f"Получены данные: {message.web_app_data.data}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    telegram_id = request.form.get('telegram_id')
    name = request.form.get('name')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (telegram_id, name) VALUES (?, ?)', (telegram_id, name))
    conn.commit()
    conn.close()

    return "✅ Пользователь добавлен!"

# === Логика бота ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Это Telegram MiniApp бот.\n\n"
        "Открой мини-приложение по кнопке ниже 👇",
        reply_markup=telebot.types.InlineKeyboardMarkup().add(
            telebot.types.InlineKeyboardButton("🚀 Открыть MiniApp", web_app=telebot.types.WebAppInfo("https://example.vercel.app"))
        )
    )

# === Запуск бота в отдельном потоке ===
def run_bot():
    bot.polling(none_stop=True)

# === Запуск Flask ===

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


