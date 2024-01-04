import telebot
from telebot import types
import webbrowser
from info import quiz, capybaras
import json
import os


token = "Your Token"
bot = telebot.TeleBot(token)


def load_user_data():
    with open("user_data.json", "r", encoding='utf8') as file:
        return json.load(file)


def save_user_data(user_data):
    with open("user_data.json", "w", encoding='utf8') as file:
        json.dump(user_data, file, ensure_ascii=False)


if os.path.exists("user_data.json"):
    user_data = load_user_data()
else:
    user_data = {}


@bot.message_handler(commands=['start'])
def lets_start(message):
    user_data[message.chat.id] = {capybara: 0 for capybara in capybaras}
    user_data[message.chat.id]["question_number"] = 0
    bot.send_message(message.chat.id, f'Приветствую,'
                                      f' {message.from_user.first_name} ({message.from_user.username})! '
                                      f'Я бот-анкета. Пройди меня и узнай <b>какая ты капибара!</b>',
                     parse_mode='html')
    send_question(message.chat.id)
    save_user_data(user_data)


def send_question(chat_id):
    questions_index = user_data[chat_id]["question_number"]
    question, options = quiz[questions_index]
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
    for text, _ in options:
        markup.add(text)
    bot.send_message(chat_id, question, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def answer(message):
    if message.chat.id not in user_data:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, начните анкету с помощью команды /start",
        )
        return
    chat_id = message.chat.id
    question_index = user_data[chat_id]["question_number"]
    _, options = quiz[question_index]
    selected_option = next(
        (scores for text, scores in options if text == message.text), None
    )
    if not selected_option:
        bot.send_message(
            chat_id, "Пожалуйста, выберите один из предложенных вариантов."
        )
        return
    for capybara, score in selected_option.items():
        user_data[chat_id][capybara] += score
    user_data[chat_id]["question_number"] += 1
    if user_data[chat_id]["question_number"] < len(quiz):
        send_question(chat_id)
    else:
        send_result(chat_id)
    save_user_data(user_data)


def send_result(chat_id):
    scores = {
        capybara: score
        for capybara, score in user_data[chat_id].items()
        if capybara != "question_number"
    }
    max_capybara = max(scores, key=scores.get)
    description, image_name = capybaras[max_capybara]
    caption_message = f"Ваш персонаж: {max_capybara}\n{description}"
    with open(image_name, "rb") as image:
        bot.send_photo(chat_id, image, caption=caption_message)
    del user_data[chat_id]
    save_user_data(user_data)


@bot.message_handler(commands=['help'])
def help_info(message):
    bot.send_message(message.chat.id, 'Пройдя данный тест вы узнаете <b>какая вы капибара!</b>\n'
                                      'Список команд, которые умеет выполнять бот:\n'
                                      '/start - начало работы анкеты или откат к началу анкеты;\n'
                                      '/help - вывести возможности бота;\n'
                                      '/git и /github - открыть профиль с другими моими проектами на GitHub;\n',
                     parse_mode='html')


@bot.message_handler(commands=['git', 'github'])
def git(message):
    webbrowser.open('https://github.com/Skylor26')


@bot.message_handler()
def no_command(message):
    if message.text != '/start' or '/help':
        bot.send_message(message.chat.id, f'Команды "<b>{message.text}</b>" несуществует. '
                                          f'Пожалуйста, введите существующую команду. '
                                          f'Список существующих команд: \n'
                                          f'/start (начало программы);\n'
                                          f'/help (способности программы)\n'
                                          f'/git и /github (другие мои проекты)', parse_mode='html')


# 3 функции ниже являются защитой формата


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    bot.reply_to(message, 'Какое красивое фото, но всё-таки пройдите анкету.')


@bot.message_handler(content_types=['video'])
def get_video(message):
    bot.reply_to(message, 'Какое замечательное видео, но всё-таки пройдите анкету.')


@bot.message_handler(content_types=['audio'])
def get_audio(message):
    bot.reply_to(message, 'Какое прекрасное звучание, но всё-таки пройдите анкету.')


bot.infinity_polling()
