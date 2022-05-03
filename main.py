from random import randrange, choice

from flask import Flask, request
from bs4 import BeautifulSoup
import requests
import logging
from custom_dict import CustomDict
from phrases import *
from rest import *

import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = CustomDict()


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if user_id not in sessionStorage:
        sessionStorage[user_id] = CustomDict(
            new_user=True,
            curr_game=None,
            mentally_math=CustomDict(first=True, level=1, amount=0, correct_amount=0,
                                     curr_answer=None, game_started=False),
            capitals=CustomDict(first=True, curr_couple=None, amount=0, attempt=0,
                                correct_amount=0, game_started=False),
            translator=CustomDict(first=True, amount=0, correct_amount=0,
                                  curr_answer=None, game_started=False),
            problems=CustomDict(first=True),
            proverbs=CustomDict(first=True)
        )

    if req['session']['new']:

        if sessionStorage[user_id].new_user:
            res['response']['text'] = START_PHRASE
        else:
            res['response']['text'] = "Я снова рада вас видеть! Что хотите попробовать на этот раз?"
        get_modes(res)

        return

    req_message = req['request']['nlu']['tokens']

    if any([i in req_message for i in ('арифметика', 'математика', 'счёт', 'счет')]):
        if sessionStorage[user_id].mentally_math.first:
            res['response']['text'] = START_MENTALLY_MATH
            sessionStorage[user_id].mentally_math.first = False
        else:
            res['response']['text'] = "Я вижу вам понравились мои примеры. Давайте порешаем еще."

        sessionStorage[user_id].curr_game = play_mentally_math
        play_mentally_math(req, res, user_id)

    elif any([i in req_message for i in ('столицы', 'страны', 'география')]):
        if sessionStorage[user_id].capitals.first:
            res['response']['text'] = START_CAPITALS
            sessionStorage[user_id].capitals.first = False
        else:
            res['response']['text'] = "Что ж, давай снова потягаемся!"

        sessionStorage[user_id].curr_game = play_capitals
        play_capitals(req, res, user_id)

    elif any([i in req_message for i in ('перевод', 'слов', 'английский')]):
        if sessionStorage[user_id].translator.first:
            res['response']['text'] = START_TRANSLATOR
            sessionStorage[user_id].translator.first = False
        else:
            res['response']['text'] = "Решили снова пополнить словарный запас? Давайте поучим новые слова..."

        sessionStorage[user_id].curr_game = play_translator
        play_translator(req, res, user_id)

    elif any([i in req_message for i in ('поговорки', 'пословицы', 'выражения')]):
        if sessionStorage[user_id].proverbs.first:
            res['response']['text'] = ""
            sessionStorage[user_id].proverbs.first = False
        else:
            res['response']['text'] = ""

    elif any([i in req_message for i in ('задачи', 'что?где?когда', 'телеигра')]):
        if sessionStorage[user_id].problems.first:
            res['response']['text'] = START_PROBLEMS
            sessionStorage[user_id].problems.first = False
        else:
            res['response']['text'] = CONTINUE_PROBLEMS

    elif any([i in req_message for i in HELP_PHRASES]):
        res['response']['text'] = ""

    elif 'что ты умеешь' in req_message:
        res['response']['text'] = ""
    else:
        sessionStorage[user_id].curr_game(req, res, user_id)


def play_mentally_math(req, res, user_id):
    level = sessionStorage[user_id].mentally_math.level

    if sessionStorage[user_id].mentally_math.game_started:
        if any([i in req['request']['nlu']['tokens'] for i in STOP_GAME_PHRASES]):
            pass
        elif sessionStorage[user_id].mentally_math.curr_answer in req['request']['original_utterance']:
            sessionStorage[user_id].mentally_math.correct_amount += 1
            res['response']['text'] = choice(CORRECT_ANSWERS_MATH)
        else:
            res['response']['text'] = choice(INCORRECT_ANSWERS_MATH) + sessionStorage[user_id].mentally_math.curr_answer
        sessionStorage[user_id].mentally_math.amount += 1
    else:
        sessionStorage[user_id].mentally_math.game_started = True

    if level == 1:
        expression = str(randrange(10, 101)) + choice(['+', '-']) + str(randrange(10, 101))
    elif level == 2:
        expression = str(randrange(1, 11)) + '*' + str(randrange(1, 11))
    elif level == 3:
        expression = str(randrange(10, 1001)) + choice(['+', '-']) + str(randrange(10, 1001))
    elif level == 4:
        dividend, divider = randrange(1, 501), randrange(1, 501)
        while dividend % divider != 0:
            dividend, divider = randrange(1, 501), randrange(1, 501)
        expression = str(dividend) + '/' + str(divider)
    else:
        operand = choice(['+', '-', '*', '/'])
        if operand in ('+', '-'):
            expression = str(randrange(1, 5201)) + choice(['+', '-']) + str(randrange(1, 5201))
        elif operand == '*':
            expression = str(randrange(1, 101)) + '*' + str(randrange(1, 11))
        else:
            dividend, divider = randrange(1, 1001), randrange(1, 1001)
            while dividend % divider != 0:
                dividend, divider = randrange(1, 1001), randrange(1, 1001)
            expression = str(dividend) + '/' + str(divider)

    sessionStorage[user_id].mentally_math.curr_answer = str(eval(expression))
    res['response']['text'] += '\n\n' + expression

    print(sessionStorage[user_id])

    if sessionStorage[user_id].mentally_math.amount == 10:
        if sessionStorage[user_id].mentally_math.correct_amount >= 6:
            sessionStorage[user_id].mentally_math.level = min(level + 1, 5)
            res['response'][
                'text'] = choice(CONGRATULATIONS_PHRASES) + f"Из последних 10 примеров " \
                                                            f"{sessionStorage[user_id].mentally_math.correct_amount} " \
                                                            f"вы решили правильно. Теперь буду давать " \
                                                            f"выражения посложнее."
        else:
            res['response'][
                'text'] = choice(LOSE_PHRASES) + "Вы допустили слишком много ошибок. Думаю пока не буду усложнять " \
                                                 "примеры. Вам нужно еще немного потренироваться."
        sessionStorage[user_id].mentally_math.amount = 0
        sessionStorage[user_id].mentally_math.correct_amount = 0


def play_capitals(req, res, user_id):
    print(sessionStorage[user_id])
    url = "http://ostranah.ru/_lists/capitals.php"

    if sessionStorage[user_id].capitals.game_started:
        if any([i in req['request']['nlu']['tokens'] for i in STOP_GAME_PHRASES]):
            pass
        if ' '.join(sessionStorage[user_id].capitals.curr_couple[:-1]).lower() == get_country(req) \
                or ' '.join(sessionStorage[user_id].capitals.curr_couple[:-1]).lower() in req['request']['original_utterance']:
            sessionStorage[user_id].capitals.correct_amount += 1
            res['response']['text'] = choice(CORRECT_ANSWERS_CAPITALS) + \
                                      ' '.join(sessionStorage[user_id].capitals.curr_couple[:-1])
            if sessionStorage[user_id].capitals.attempt == 1:
                sessionStorage[user_id].capitals.attempt = 0
        else:
            if sessionStorage[user_id].capitals.attempt == 0:
                sessionStorage[user_id].capitals.attempt += 1
                res['response']['text'] = choice(ATTEMPTS_PHRASES)
                return
            else:
                sessionStorage[user_id].capitals.attempt = 0
                res['response']['text'] = choice(INCORRECT_ANSWERS_MATH) + \
                                          ' '.join(sessionStorage[user_id].capitals.curr_couple[:-1])
        sessionStorage[user_id].capitals.amount += 1
    else:
        sessionStorage[user_id].capitals.game_started = True

    response = requests.get(url)

    if not response:
        res["response"]["text"] = "Ой! Кажется что-то пошло не так!"
        return

    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('tr')

    couple = quotes[randrange(1, 193)].text.split()
    while couple == sessionStorage[user_id].capitals.curr_couple and ' '.join(couple[:-1]) != "Науру":
        couple = quotes[randrange(1, 193)].text.split()

    sessionStorage[user_id].capitals.curr_couple = couple
    res['response']['text'] += '\n\n' + couple[-1]
    print(sessionStorage[user_id])

    if sessionStorage[user_id].capitals.amount == 10:
        res['response']['text'] += "Еще не устали?"


def play_translator(req, res, user_id):
    if sessionStorage[user_id].translator.game_started:
        if any([i in req['request']['nlu']['tokens'] for i in STOP_GAME_PHRASES]):
            pass
        elif 'режим' in req['request']['nlu']['tokens']:
            pass
        if sessionStorage[user_id].translator.curr_answer in req['request']['nlu']['tokens']:
            sessionStorage[user_id].translator.correct_amount += 1
            res['response']['text'] = choice(CORRECT_ANSWERS_CAPITALS) + sessionStorage[user_id].translator.curr_answer
        else:
            res['response']['text'] = choice(INCORRECT_ANSWERS_MATH) + sessionStorage[user_id].translator.curr_answer
        sessionStorage[user_id].translator.amount += 1
    else:
        sessionStorage[user_id].translator.game_started = True

    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"

    params = {"langpair": "ru|en", "q": None, "mt": "1", "onlyprivate": "0", "de": "a@b.c"}

    headers = {
        'x-rapidapi-key': "1e969770a5msh5896a54cd19e719p155db8jsnf0d1e659764f",
        'x-rapidapi-host': "translated-mymemory---translation-memory.p.rapidapi.com"
    }
    params["q"] = None
    response = requests.get(url, headers=headers, params=params)
    if not response:
        res["response"]["text"] = "Ой! Кажется что-то пошло не так!"
        return
    json_response = response.json()
    translated_text = json_response["responseData"]["translatedText"]
    sessionStorage[user_id].translator.curr_answer = translated_text


if __name__ == '__main__':
    app.run()
