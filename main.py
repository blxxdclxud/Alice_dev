import json
import logging
from json import load
from random import randrange, choice

import requests
from bs4 import BeautifulSoup
from flask import Blueprint, request, Flask

from custom_dict import CustomDict
from phrases import *
from rest import *


app = Flask(__name__)
alice_dev = Blueprint(
    'alice_dev',
    __name__
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='alice.log')
logger = logging.getLogger(__name__)

sessionStorage = CustomDict()


@alice_dev.route('/post', methods=['POST'])
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
            choose=False,
            mentally_math=CustomDict(first=True, level=1, amount=0,
                                     correct_amount=0,
                                     curr_answer=None, game_started=False),
            capitals=CustomDict(first=True, curr_couple=None, amount=0,
                                attempt=0,
                                correct_amount=0, game_started=False),
            translator=CustomDict(first=True, amount=0, correct_amount=0,
                                  curr_answer=None, game_started=False),
            proverbs=CustomDict(first=True, amount=0, correct_amount=0,
                                curr_answer=None, game_started=False)
        )

    if req['session']['new']:

        if sessionStorage[user_id].new_user:
            res['response']['text'] = START_PHRASE
            res['response']['tts'] = START_PHRASE[-1]
        else:
            res['response']['text'] = GREETING_AGAIN
            res['response']['tts'] = GREETING_AGAIN[-1]
        sessionStorage[user_id].choose = True
        return

    req_message = ' '.join(req['request']['nlu']['tokens'])

    if sessionStorage[user_id].choose:
        if any([i in req_message for i in ACCEPT]):
            res['response']['text'] = "Вот все режимы:"
            get_modes(res)
            get_buttons(res)
            sessionStorage[user_id].choose = False
        elif any([i in req_message for i in REJECT]):
            res['response']['text'] = CLOSE_PHRASE
            res['response']['tts'] = CLOSE_PHRASE
            res['response']['end_session'] = True
            sessionStorage[user_id].choose = False
        else:
            reply = choice(MISUNDERSTOOD)
            res['response']['text'] = reply[0]
            res['response']['tts'] = reply[-1]
        return

    if any([i in req_message for i in ('арифметик', 'матем', 'счёт', 'счет')]):
        if sessionStorage[user_id].mentally_math.first:
            res['response']['text'] = START_MENTALLY_MATH
            get_buttons(res)
            res['response']['tts'] = START_MENTALLY_MATH[-1]
            sessionStorage[user_id].mentally_math.first = False
        else:
            res['response']['text'] = MENTALLY_MATH_AGAIN
            get_buttons(res)
            res['response']['tts'] = MENTALLY_MATH_AGAIN[-1]

        sessionStorage[user_id].curr_game = play_mentally_math
        play_mentally_math(req, res, user_id)

    elif any([i in req_message for i in ('столиц', 'стран', 'географи')]):
        if sessionStorage[user_id].capitals.first:
            res['response']['text'] = START_CAPITALS
            get_buttons(res)
            res['response']['tts'] = START_CAPITALS[-1]
            sessionStorage[user_id].capitals.first = False
        else:
            reply = "Что ж, давай снова потягаемся!"
            res['response']['text'] = reply
            get_buttons(res)
            res['response']['tts'] = reply[-1]

        sessionStorage[user_id].curr_game = play_capitals
        play_capitals(req, res, user_id)

    elif any([i in req_message for i in ('перев', 'англ')]):
        if sessionStorage[user_id].translator.first:
            res['response']['text'] = START_TRANSLATOR
            get_buttons(res)
            sessionStorage[user_id].translator.first = False
            res['response']['tts'] = START_TRANSLATOR[-1]
        else:
            res['response']['text'] = TRANSLATOR_AGAIN
            get_buttons(res)
            res['response']['tts'] = TRANSLATOR_AGAIN[-1]

        sessionStorage[user_id].curr_game = play_translator
        play_translator(req, res, user_id)

    elif any([i in req_message for i in ('поговор', 'послов', 'выражен')]):
        if sessionStorage[user_id].proverbs.first:
            res['response']['text'] = START_PROVERB
            get_buttons(res)
            res['response']['tts'] = START_PROVERB[-1]
            sessionStorage[user_id].proverbs.first = False
        else:
            res['response']['text'] = PROVERB_AGAIN
            get_buttons(res)
            res['response']['tts'] = PROVERB_AGAIN[-1]

        sessionStorage[user_id].curr_game = play_proverbs
        play_proverbs(req, res, user_id)

    elif any([i[0] in req_message for i in HELP_PHRASES]):
        res['response']['text'] = HELP_PHRASE
        get_buttons(res)
        res['response']['tts'] = HELP_PHRASE[-1]

    elif 'что ты умеешь' in req_message:
        res['response']['text'] = WHAT_CAN_YOU_DO_PHRASE
        get_buttons(res)
        res['response']['tts'] = WHAT_CAN_YOU_DO_PHRASE[-1]
    elif 'режим' in req_message:
        res['response']['text'] = "Вот все режимы:"
        get_modes(res)
        get_buttons(res)
    elif any(i[0].lower() in req_message for i in STOP_GAME_PHRASES):
        res['response']['text'] = CLOSE_PHRASE
        res['response']['tts'] = CLOSE_PHRASE
        res['response']['end_session'] = True
    else:
        sessionStorage[user_id].curr_game(req, res, user_id)


def play_mentally_math(req, res, user_id):
    level = sessionStorage[user_id].mentally_math.level

    if sessionStorage[user_id].mentally_math.game_started:
        if any([i in req['request']['nlu']['tokens'] for i in
                STOP_GAME_PHRASES]):
            pass
        elif sessionStorage[user_id].mentally_math.curr_answer in \
                req['request']['original_utterance']:
            sessionStorage[user_id].mentally_math.correct_amount += 1
            reply = choice(CORRECT_ANSWERS_MATH)[0]
            res['response']['text'] = reply
            get_buttons(res)
            res['response']['tts'] = reply[-1]
        else:
            reply = choice(INCORRECT_ANSWERS_MATH)[0] + sessionStorage[
                user_id].mentally_math.curr_answer
            res['response']['text'] = reply
            res['response']['tts'] = reply[-1]
        sessionStorage[user_id].mentally_math.amount += 1
    else:
        reset_params('mentally_math', user_id)
        sessionStorage[user_id].mentally_math.game_started = True

    if level == 1:
        expression = str(randrange(10, 101)) + choice(['+', '-']) + str(
            randrange(10, 101))
    elif level == 2:
        expression = str(randrange(1, 11)) + '*' + str(randrange(1, 11))
    elif level == 3:
        expression = str(randrange(10, 1001)) + choice(['+', '-']) + str(
            randrange(10, 1001))
    elif level == 4:
        dividend, divider = randrange(1, 501), randrange(1, 501)
        while dividend % divider != 0:
            dividend, divider = randrange(1, 501), randrange(1, 501)
        expression = str(dividend) + '/' + str(divider)
    else:
        operand = choice(['+', '-', '*', '/'])
        if operand in ('+', '-'):
            expression = str(randrange(1, 5201)) + choice(['+', '-']) + str(
                randrange(1, 5201))
        elif operand == '*':
            expression = str(randrange(1, 101)) + '*' + str(randrange(1, 11))
        else:
            dividend, divider = randrange(1, 1001), randrange(1, 1001)
            while dividend % divider != 0:
                dividend, divider = randrange(1, 1001), randrange(1, 1001)
            expression = str(dividend) + '/' + str(divider)

    sessionStorage[user_id].mentally_math.curr_answer = str(eval(expression))
    res['response']['text'] += ' \n\n ' + expression
    get_buttons(res)
    res['response']['tts'] = expression

    print(sessionStorage[user_id])

    if sessionStorage[user_id].mentally_math.amount == 6:
        if sessionStorage[user_id].mentally_math.correct_amount >= 3:
            sessionStorage[user_id].mentally_math.level = min(level + 1, 5)
            reply = choice(CONGRATULATIONS_PHRASES)[
                        0] + f"Из последних 6 примеров " \
                             f"{sessionStorage[user_id].mentally_math.correct_amount} " \
                             f"вы решили правильно. Теперь буду давать " \
                             f"выражения посложнее."
            res['response']['text'] = reply
            get_buttons(res)
            res['response']['tts'] = reply[-1]
        else:
            reply = choice(LOSE_PHRASES)[
                        0] + "Вы допустили слишком много ошибок. Думаю пока не буду усложнять " \
                             "примеры. Вам нужно еще немного потренироваться."
            res['response']['text'] = reply
            get_buttons(res)
            res['response']['tts'] = reply[-1]
        sessionStorage[user_id].mentally_math.amount = 0
        sessionStorage[user_id].mentally_math.correct_amount = 0


def play_capitals(req, res, user_id):
    print(sessionStorage[user_id])
    url = "http://ostranah.ru/_lists/capitals.php"

    if sessionStorage[user_id].capitals.game_started:
        if any([i in req['request']['nlu']['tokens'] for i in
                STOP_GAME_PHRASES]):
            pass
        if ' '.join(sessionStorage[user_id].capitals.curr_couple[:-1]).lower() == get_country(req) \
                or ' '.join(sessionStorage[user_id].capitals.curr_couple[:-1]).lower() in ' '.join(req['request']['nlu'][
            'tokens']):
            sessionStorage[user_id].capitals.correct_amount += 1
            reply = choice(CORRECT_ANSWERS)[0] + \
                    ' '.join(sessionStorage[user_id].capitals.curr_couple[:-1]) + choice(NEXT_PHRASES)[0]
            res['response']['text'] = reply
            get_buttons(res)
            res['response']['tts'] = reply[-1]
            if sessionStorage[user_id].capitals.attempt == 1:
                sessionStorage[user_id].capitals.attempt = 0
        else:
            if sessionStorage[user_id].capitals.attempt == 0:
                sessionStorage[user_id].capitals.attempt += 1
                reply = choice(ATTEMPTS_PHRASES)[0]
                res['response']['text'] = reply
                get_buttons(res)
                res['response']['tts'] = reply[-1]
                return
            else:
                sessionStorage[user_id].capitals.attempt = 0
                reply = choice(INCORRECT_ANSWERS_MATH)[0] + \
                        ' '.join(
                            sessionStorage[user_id].capitals.curr_couple[:-1])
                res['response']['text'] = reply
                get_buttons(res)
                res['response']['tts'] = reply[-1]
        sessionStorage[user_id].capitals.amount += 1
    else:
        reset_params('capitals', user_id)
        sessionStorage[user_id].capitals.game_started = True

    response = requests.get(url)

    if not response:
        res["response"]["text"] = SOMETHING_WRONG
        res['response']['tts'] = SOMETHING_WRONG[-1]
        return

    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('tr')

    couple = quotes[randrange(1, 193)].text.split()
    while couple == sessionStorage[user_id].capitals.curr_couple and ' '.join(couple[:-1]) != "Науру":
        couple = quotes[randrange(1, 193)].text.split()

    sessionStorage[user_id].capitals.curr_couple = couple
    res['response']['text'] += ' \n\n ' + couple[-1]
    get_buttons(res)
    res['response']['tts'] += couple[-1]
    print(sessionStorage[user_id])


def play_translator(req, res, user_id):
    get_translator_modes(res)
    if sessionStorage[user_id].translator.game_started:
        if any([i in ' '.join(req['request']['nlu']['tokens']) for i in
                sessionStorage[user_id].translator.curr_answer.split(', ')]):
            sessionStorage[user_id].translator.correct_amount += 1

            reply = choice(CORRECT_ANSWERS)[0] + sessionStorage[
                user_id].translator.curr_answer + choice(NEXT_PHRASES)[0]
            res['response']['text'] = reply
            get_buttons(res)
            res['response']['tts'] = reply[-1]
        else:
            reply = choice(INCORRECT_ANSWERS_MATH)[0] + sessionStorage[
                user_id].translator.curr_answer
            res['response']['text'] = reply
            get_buttons(res)
            res['response']['tts'] = reply[-1]
        sessionStorage[user_id].translator.amount += 1
    else:
        reset_params('translator', user_id)
        sessionStorage[user_id].translator.game_started = True

    with open("words.json", 'rt') as file:
        json_words = load(file)

        word = choice(list(json_words.keys()))
        couple = [word, json_words[word]]
        while couple == sessionStorage[user_id].translator.curr_answer:
            word = choice(json_words.keys())
            couple = [word, json_words[word]]

    sessionStorage[user_id].translator.curr_answer = couple[-1]
    res['response']['text'] += ' \n\n ' + couple[0]
    get_buttons(res)
    res['response']['tts'] = couple[0]
    print(sessionStorage[user_id])


def play_proverbs(req, res, user_id):
    url = "http://iamruss.ru/famous-russian-proverb/"

    if sessionStorage[user_id].proverbs.game_started:
        if any([i in req['request']['nlu']['tokens'] for i in STOP_GAME_PHRASES]):
            pass
        if (sessionStorage[user_id].proverbs.curr_answer.split()[-1].replace('ё', 'е') or
            sessionStorage[user_id].proverbs.curr_answer.split()[-1]) in req['request']['nlu'][
            'tokens']:
            sessionStorage[user_id].proverbs.correct_amount += 1
            reply = choice(CORRECT_ANSWERS_CAPITALS)[0] + sessionStorage[
                user_id].proverbs.curr_answer
            res['response']['text'] = reply
            get_buttons(res)
            res['response']['tts'] = reply[-1]
        else:
            reply = choice(INCORRECT_ANSWERS_MATH)[0] + sessionStorage[
                user_id].proverbs.curr_answer
            res['response']['text'] = reply
            get_buttons(res)
            res['response']['tts'] = reply[-1]
        sessionStorage[user_id].proverbs.amount += 1
    else:
        sessionStorage[user_id].proverbs.game_started = True

    response = requests.get(url)

    if not response:
        res["response"]["text"] = SOMETHING_WRONG
        res['response']['tts'] = SOMETHING_WRONG
        return

    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('td')

    proverb = quotes[randrange(0, 319)].text
    while proverb == sessionStorage[user_id].capitals.curr_answer:
        proverb = quotes[randrange(0, 319)].text

    sessionStorage[user_id].proverbs.curr_answer = proverb

    res['response']['text'] += ' \n\n ' + ' '.join(proverb.split()[:-1])
    get_buttons(res)
    res['response']['tts'] = ' '.join(proverb.split()[:-1])
    print(sessionStorage[user_id])


def reset_params(exc, user_id):
    for game in list(sessionStorage[user_id].keys())[3:]:
        if game != exc:
            sessionStorage[user_id][game].game_started = False
        if 'attempt' in game:
            sessionStorage[user_id][game].attempt = 0


if __name__ == '__main__':
    app.register_blueprint(alice_dev)
    app.run()
