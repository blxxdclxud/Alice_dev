def get_modes(res):
    res['response']['card'] = {}
    res['response']['card']['type'] = "ItemsList"
    res['response']['card']['items'] = [
        {
            "image_id": "1652229/bd5bb3d640d0bfc7c0f8",
            "title": "Ментальная арифметика",
            "description": "Я проверю ваши навыки устного счета.",
            "button": {
                "text": "Ментальная арифметика"
            }
        },
        {
            "image_id": "937455/e7fb747d5dd3bbd49136",
            "title": "Столицы государств",
            "description": "Вы будете угадывать страны по их столицам.",
            "button": {
                "text": "Столицы государств"
            }
        },
        {
            "image_id": "965417/a488d4c296b35614bb6c",
            "title": "Перевод слов",
            "description": "Я даю вам слово, а вы мне его переводите.",
            "button": {
                "text": "Перевод слов"
            }
        },
        {
            "image_id": "1652229/39ba63bea2ab7e90a659",
            "title": "Изучение поговорок",
            "description": "Вы должны закончить поговорки.",
            "button": {
                "text": "Изучение поговорок"
            }
        }
    ]


def get_country(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('country', None)


def get_number(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.NUMBER':
            return entity['value'].get('value', None)


def get_buttons(res):
    res['response']['buttons'] = [{
        'title': 'Помощь',
        'hide': True
    }, {
        'title': 'Что ты умеешь?',
        'hide': True
    },
        {
            'title': 'Выход',
            'hide': True
        },
        {
            'title': 'Режимы',
            'hide': True
        }]
