from pywebio.input import *
from pywebio.output import *
import math
import prices
import messages

put_markdown("# Планування шкільної поїздки")

uchni = int(input("Кількість учнів"))
vchyteli = int(input("Кількість вчителів"))

transport = radio(
    "Оберіть транспорт",
    options=["Автобус", "Поїзд"]
)

dni = slider("Кількість днів", min_value=0, max_value=10)

if uchni == 0:
    put_error(messages.ERROR_TEXT)

else:
    people = uchni + vchyteli

    if dni == 0:
        hotel = 0
    else:
        hotel = people * prices.HOTEL_PRICE * dni

    if transport == "Автобус":
        buses = math.ceil(people / 40)
        transport_price = buses * prices.BUS_PRICE
    else:
        buses = 0
        transport_price = people * prices.TRAIN_PRICE * 2

    total = transport_price + hotel

    if people > 30:
        total = total * 0.9

    put_success(messages.SUCCESS_TEXT)

    put_text(f"Людей: {people}")

    if transport == "Автобус":
        put_text(f"Автобусів потрібно: {buses}")

    put_text(f"Транспорт: {transport_price} грн")
    put_text(f"Проживання: {hotel} грн")
    put_text(f"Загальна сума: {total} грн")