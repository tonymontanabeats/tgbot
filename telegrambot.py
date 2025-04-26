import telebot
from telebot import types
import webbrowser
import random
import textwrap
import re
import os

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# Глобальные переменные для очереди
shuffled_phrases = []
current_index = 0
BOT_USERNAME = 'djprognoz_bot'  # замени на своего


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Привет! Я - музыкальный ясновидящий бот и могу предсказывать будущее. Могу погадать в личке через команду /future, но лучше всего вызывай меня в групповом чате с твоими друзьями через @djprognoz_bot')


def load_and_shuffle_phrases():
    with open('phrases.txt', 'r', encoding='UTF-8') as file:
        phrases = [line.strip() for line in file if line.strip()]
    random.shuffle(phrases)
    return phrases


@bot.inline_handler(func=lambda query: True)
def inline_query_handler(inline_query):
    try:
        # Получаем данные пользователя, который инициировал запрос
        user_name = inline_query.from_user.username or inline_query.from_user.first_name or "гость"

        # Загрузка фраз из файла
        phrases = load_and_shuffle_phrases()

        # Выбираем случайную фразу
        random_phrase = random.choice(phrases)

        # Обработка текста и музыки
        music_match = re.search(r'(Музыка:|Music:)\s*(.*?)\s*\|\s*(https?://[^\s]+)', random_phrase, re.IGNORECASE)
        if music_match:
            track_name = music_match.group(2).strip()
            track_link = music_match.group(3).strip()
            main_text = random_phrase[:music_match.start()].strip()
        else:
            track_name = ""
            track_link = ""
            main_text = random_phrase

        # Разбиваем текст на предложения
        sentences = re.split(r'(?<=[.!?]) +', main_text)
        if len(sentences) > 1:
            main = " ".join(sentences[:-1]).strip()
            last = sentences[-1].strip()
            formatted = f"{main}{last}"
        else:
            formatted = f"{main_text}"

        # Блок музыки
        if track_name and track_link:
            music_block = f"\n\n*Музыка: {track_name}*\n[🎧 Послушать трек]({track_link})"
        else:
            music_block = ""

        # Формирование финального сообщения с обращением к пользователю
        text = f"🔮 Вот предсказание для @{user_name}:\n\n{formatted}{music_block}"

        # Создаём инлайн-результат
        result = types.InlineQueryResultArticle(
            id='1',
            title="Получить предсказание",
            input_message_content=types.InputTextMessageContent(
                message_text=text,
                parse_mode='Markdown'
            ),
            description="Нажми, чтобы получить предсказание",
            thumbnail_url="https://i.imgur.com/4M34hi2.png"  # можно добавить иконку
        )

        bot.answer_inline_query(inline_query.id, [result], cache_time=1)
    except Exception as e:
        print(e)


@bot.message_handler(commands=['future'])
def future(message):
    chat_type = message.chat.type
    user = message.from_user
    command_text = message.text.lower()

    # Имя пользователя
    user_name = user.username or user.first_name or "гость"
    # В группах — проверка: есть ли упоминание именно этого бота
    if chat_type in ['group', 'supergroup']:
        if f'/future@{BOT_USERNAME.lower()}' not in command_text:
            return  # Не обрабатываем команды без точного тега

    # Тип чата: private, group, supergroup, channel
    if chat_type == "private":
        greeting = f"🔮 @{user_name}, Предсказание для тебя:"
    elif chat_type in ["group", "supergroup"]:
        greeting = f"🔮 Предсказание для @{user_name} в группе"
    else:
        greeting = f"🔮 Предсказание!"

    # Далее — обычная логика генерации предсказания
    with open('phrases.txt', 'r', encoding='UTF-8') as file:
        phrases = [line.strip() for line in file if line.strip()]

    # Перетасовка и выбор без повторов — можно вставить свою очередь тут
    random_phrase = random.choice(phrases)

    # Обработка текста и музыки
    music_match = re.search(r'(Музыка:|Music:)\s*(.*?)\s*\|\s*(https?://[^\s]+)', random_phrase, re.IGNORECASE)
    if music_match:
        track_name = music_match.group(2).strip()
        track_link = music_match.group(3).strip()
        main_text = random_phrase[:music_match.start()].strip()
    else:
        track_name = ""
        track_link = ""
        main_text = random_phrase

    # Делим на предложения
    sentences = re.split(r'(?<=[.!?]) +', main_text)
    if len(sentences) > 1:
        main = " ".join(sentences[:-1]).strip()
        last = sentences[-1].strip()
        formatted = f"{main}{last}"
    else:
        formatted = f"{main_text}"

    # Блок музыки
    if track_name and track_link:
        music_block = f"\n\n*Музыка: {track_name}*\n[🎧 Послушать трек]({track_link})"
    else:
        music_block = ""

    # Финальное сообщение
    final_message = f"{greeting}\n\n{formatted}{music_block}"

    bot.reply_to(message, final_message, parse_mode='Markdown')


bot.polling(none_stop=True)