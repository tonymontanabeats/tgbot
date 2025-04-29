import telebot
from telebot import types
import random
import re
import os

# Токен бота
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# Username бота без @
BOT_USERNAME = 'djprognoz_bot'

# Функция для загрузки и перемешивания фраз
def load_and_shuffle_phrases():
    with open('phrases.txt', 'r', encoding='UTF-8') as file:
        phrases = [line.strip() for line in file if line.strip()]
    random.shuffle(phrases)
    return phrases

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Привет! Я - музыкальный ясновидящий бот и могу предсказывать будущее. '
        'Могу погадать в личке через команду /future, но лучше всего вызывай меня '
        'в групповом чате через @djprognoz_bot'
    )

# Обработчик инлайн-запросов
@bot.inline_handler(func=lambda query: True)
def inline_query_handler(inline_query):
    try:
        user_name = inline_query.from_user.username or inline_query.from_user.first_name or "гость"
        phrases = load_and_shuffle_phrases()
        random_phrase = random.choice(phrases)

        music_match = re.search(r'(Музыка:|Music:)\s*(.*?)\s*\|\s*(https?://[^\s]+)', random_phrase, re.IGNORECASE)
        if music_match:
            track_name = music_match.group(2).strip()
            track_link = music_match.group(3).strip()
            main_text = random_phrase[:music_match.start()].strip()
        else:
            track_name = ""
            track_link = ""
            main_text = random_phrase

        sentences = re.split(r'(?<=[.!?]) +', main_text)
        formatted = " ".join(sentences) if len(sentences) > 1 else main_text

        music_block = f"\n\n*Музыка: {track_name}*\n[🎧 Послушать трек]({track_link})" if track_name and track_link else ""
        text = f"🔮 Вот предсказание для @{user_name}:\n\n{formatted}{music_block}"

        result = types.InlineQueryResultArticle(
            id='1',
            title="Получить предсказание",
            input_message_content=types.InputTextMessageContent(
                message_text=text,
                parse_mode='Markdown'
            ),
            description="Нажми, чтобы получить предсказание",
            thumbnail_url="https://i.imgur.com/4M34hi2.png"
        )

        bot.answer_inline_query(inline_query.id, [result], cache_time=1)
    except Exception as e:
        print(e)

# Обработчик команды /future
@bot.message_handler(commands=['future'])
def future(message):
    chat_type = message.chat.type
    user = message.from_user
    command_text = message.text.lower()
    user_name = user.username or user.first_name or "гость"

    if chat_type in ['group', 'supergroup'] and f'/future@{BOT_USERNAME.lower()}' not in command_text:
        return

    greeting = f"🔮 @{user_name}, Предсказание для тебя:" if chat_type == "private" else f"🔮 Предсказание для @{user_name} в группе"
    phrases = load_and_shuffle_phrases()
    random_phrase = random.choice(phrases)

    music_match = re.search(r'(Музыка:|Music:)\s*(.*?)\s*\|\s*(https?://[^\s]+)', random_phrase, re.IGNORECASE)
    if music_match:
        track_name = music_match.group(2).strip()
        track_link = music_match.group(3).strip()
        main_text = random_phrase[:music_match.start()].strip()
    else:
        track_name = ""
        track_link = ""
        main_text = random_phrase

    sentences = re.split(r'(?<=[.!?]) +', main_text)
    formatted = " ".join(sentences) if len(sentences) > 1 else main_text
    music_block = f"\n\n*Музыка: {track_name}*\n[🎧 Послушать трек]({track_link})" if track_name and track_link else ""

    final_message = f"{greeting}\n\n{formatted}{music_block}"
    bot.reply_to(message, final_message, parse_mode='Markdown')

if __name__ == "__main__":
    bot.remove_webhook()  # ОТКЛЮЧАЕМ вебхук перед polling
    print("Бот запущен...")
    bot.polling(none_stop=True)

