import telebot
from telebot import types
from flask import Flask, request
import os
import random
import re

# Токен Telegram-бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "djprognoz_bot"
bot = telebot.TeleBot(BOT_TOKEN)

# Flask-приложение
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def receive_update():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# Загрузка фраз
def load_and_shuffle_phrases():
    with open('phrases.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    random.shuffle(lines)
    return lines

# Команда /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        'Привет! Я музыкальный ясновидящий. Используй /future или @djprognoz_bot в группе.'
    )

# Команда /future
@bot.message_handler(commands=['future'])
def future_handler(message):
    user_name = message.from_user.username or message.from_user.first_name or "гость"
    greeting = f"🔮 @{user_name}, твоё предсказание:\n\n"

    phrases = load_and_shuffle_phrases()
    phrase = random.choice(phrases)

    music_match = re.search(r'(Музыка:|Music:)\s*(.*?)\s*\|\s*(https?://[^\s]+)', phrase, re.IGNORECASE)
    if music_match:
        track_name = music_match.group(2).strip()
        track_link = music_match.group(3).strip()
        phrase = phrase[:music_match.start()].strip()
        music = f"\n\n*Музыка: {track_name}*\n[🎧 Послушать трек]({track_link})"
    else:
        music = ""

    final_text = f"{greeting}{phrase}{music}"
    bot.send_message(message.chat.id, final_text, parse_mode="Markdown")

# Обработчик inline
@bot.inline_handler(func=lambda query: True)
def inline_handler(query):
    try:
        user_name = query.from_user.username or query.from_user.first_name or "гость"
        phrases = load_and_shuffle_phrases()
        phrase = random.choice(phrases)

        music_match = re.search(r'(Музыка:|Music:)\s*(.*?)\s*\|\s*(https?://[^\s]+)', phrase, re.IGNORECASE)
        if music_match:
            track_name = music_match.group(2).strip()
            track_link = music_match.group(3).strip()
            phrase = phrase[:music_match.start()].strip()
            music = f"\n\n*Музыка: {track_name}*\n[🎧 Послушать трек]({track_link})"
        else:
            music = ""

        result_text = f"🔮 Предсказание для @{user_name}:\n\n{phrase}{music}"

        result = types.InlineQueryResultArticle(
            id='1',
            title="Получить предсказание",
            input_message_content=types.InputTextMessageContent(
                message_text=result_text,
                parse_mode="Markdown"
            ),
            description="Жми, чтобы узнать будущее",
            thumbnail_url="https://i.imgur.com/4M34hi2.png"
        )
        bot.answer_inline_query(query.id, [result], cache_time=1)
    except Exception as e:
        print(e)

bot.remove_webhook()
bot.set_webhook(url=f"{os.getenv('WEBHOOK_URL')}/{BOT_TOKEN}")
