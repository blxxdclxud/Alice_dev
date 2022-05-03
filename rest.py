def get_modes(res):
    res['response']['card'] = {}
    res['response']['card']['type'] = "ItemsList"
    res['response']['card']['items'] = [
        {
            "image_id": "1652229/bd5bb3d640d0bfc7c0f8",
            "title": "Ментальная арифметика",
            "description": "Я проверю ваши навыки устного счета.",
            "button": {
                "text": "Ментальная арифметика",
                "payload": {}
            }
        },
        {
            "image_id": "937455/e7fb747d5dd3bbd49136",
            "title": "Столицы государств",
            "description": "Вы будете угадывать страны по их столицам.",
            "button": {
                "text": "Столицы государств",
                "payload": {}
            }
        },
        {
            "image_id": "965417/a488d4c296b35614bb6c",
            "title": "Перевод слов",
            "description": "Я даю вам слово, а вы мне его переводите.",
            "button": {
                "text": "Перевод слов",
                "payload": {}
            }
        },
        {
            "image_id": "1652229/39ba63bea2ab7e90a659",
            "title": "Изучение поговорок",
            "description": "Вы должны закончить поговорки.",
            "button": {
                "text": "Изучение поговорок",
                "payload": {}
            }
        }
    ]


def get_country(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('country', None)


def get_translator_modes(res):
    res['response']['card'] = {}
    res['response']['card']['type'] = "ItemsList"
    res['response']['card']['items'] = [
        {
            "image_id": "1652229/bd5bb3d640d0bfc7c0f8",
            "title": "С русского на английский",
            "button": {
                "text": "С русского на английский",
                "payload": {}
            }
        },
        {
            "image_id": "937455/e7fb747d5dd3bbd49136",
            "title": "С английского на русский",
            "button": {
                "text": "С английского на русский",
                "payload": {}
            }
        },
        {
            "image_id": "937455/e7fb747d5dd3bbd49136",
            "title": "Без разницы) Давай вперемешку",
            "button": {
                "text": "Без разницы) Давай вперемешку",
                "payload": {}
            }
        }
    ]
