import telebot
import json
import info

bot = telebot.TeleBot(info.TOKEN)

STATE_FILE = 'state.json'

def save_state(user_id, question_index):
    state = {
        'user_id': user_id,
        'question_index': question_index
    }
    with open(STATE_FILE, 'w') as file:
        json.dump(state, file)

def load_state(user_id):
    try:
        with open(STATE_FILE, 'r') as file:
            state = json.load(file)
            if state['user_id'] == user_id:
                return state['question_index']
    except FileNotFoundError:
        pass
    return 0

@bot.message_handler(commands=['start'])
def start(message):
    question_index = load_state(message.chat.id)
    if question_index == 0:
        bot.send_message(message.chat.id, 'Привет! Давайте начнем анкету по которой мы соберем ваши данные и позже наш специалист свяжется с вами.')
    else:
        bot.send_message(message.chat.id, 'Продолжаем анкету с вопроса номер {}'.format(question_index + 1))
    ask_question(message.chat.id, question_index)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton('/restart'))
    bot.send_message(message.chat.id, 'Для перезапуска анкеты нажми /restart', reply_markup=markup)

@bot.message_handler(commands=['restart'])
def restart(message):
    save_state(message.chat.id, 0)
    bot.send_message(message.chat.id, 'Анкета была перезапущена. Начнем заново!')
    ask_question(message.chat.id, 0)

def ask_question(user_id, question_index):
    if question_index < len(info.questions):
        question = list(info.questions.keys())[question_index]
        answers = info.questions[question]
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for answer in answers:
            markup.add(telebot.types.KeyboardButton(answer))
        bot.send_message(user_id, question, reply_markup=markup)
    else:
        bot.send_message(user_id, 'Анкета завершена, спасибо!')
        bot.send_photo(user_id, open('result.jpg', 'rb'))

@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    question_index = load_state(message.chat.id)
    if question_index < len(info.questions):
        question = list(info.questions.keys())[question_index]
        answers = info.questions[question]
        if message.text in answers:
            question_index += 1
            save_state(message.chat.id, question_index)
            ask_question(message.chat.id, question_index)
        else:
            bot.send_message(message.chat.id, 'Выберите один из предложенных вариантов ответа.')
    else:
        bot.send_message(message.chat.id, 'Анкета завершена, спасибо!')
        bot.send_photo(message.chat.id, open('result.jpg', 'rb'))

#осталось реализовать сбор ответов в словарь к примеру, но дедлайн уже просрочил так что пока так :) пока думаю как сделать
#def save_answers(user_id, answers):
#    try:
#        with open('result.json', 'r') as file:
#            data = json.load(file)
#    except FileNotFoundError:
#        data = {}
#    data[str(user_id)] = answers
#    with open('result.json', 'w') as file:
#        json.dump(data, file)

bot.polling()