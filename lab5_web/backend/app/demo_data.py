"""The demo data: the lab's 9 trains (menu item 8 in lab5/python/zadanie1_poezda.py) with routes.

Plain data: the app loads it into an empty database at startup, and POST /api/demo/reset/ loads it again.
City ids are fixed: the API docs use them in their examples.
"""

from datetime import time

COUNTRIES = [
    {"code": "MD", "name": "Молдова"},
    {"code": "RO", "name": "Румыния"},
    {"code": "UA", "name": "Украина"},
    {"code": "RU", "name": "Россия"},
]

CITIES = [
    {"id": 1, "name": "Унгены", "country_code": "MD"},
    {"id": 2, "name": "Бельцы", "country_code": "MD"},
    {"id": 3, "name": "Бендеры", "country_code": "MD"},
    {"id": 4, "name": "Тирасполь", "country_code": "MD"},
    {"id": 5, "name": "Страшены", "country_code": "MD"},
    {"id": 6, "name": "Яссы", "country_code": "RO"},
    {"id": 7, "name": "Бухарест", "country_code": "RO"},
    {"id": 8, "name": "Киев", "country_code": "UA"},
    {"id": 9, "name": "Одесса", "country_code": "UA"},
    {"id": 10, "name": "Москва", "country_code": "RU"},
]

# number, destination, departure, stops in route order (city ids)
TRAINS = [
    (50, 10, time(8, 15), [2, 8]),
    (30, 7, time(21, 40), [5, 1, 6]),
    (70, 9, time(6, 5), [3, 4]),
    (20, 6, time(13, 0), [1]),
    (40, 8, time(17, 30), [2]),
    (60, 10, time(22, 50), [8]),
    (80, 1, time(10, 20), [5]),
    (35, 7, time(9, 45), [1, 6]),
    (65, 9, time(15, 10), [3]),
]


def train_rows():
    return [{"number": n, "destination_id": d, "departure": t} for n, d, t, _ in TRAINS]


def stop_rows():
    return [
        {"train_number": n, "stop_no": stop_no, "city_id": city_id}
        for n, _, _, stops in TRAINS
        for stop_no, city_id in enumerate(stops, 1)
    ]
