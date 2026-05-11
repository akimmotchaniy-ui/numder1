from pywebio.output import put_text, put_markdown
from pywebio import start_server

from toyota_info import car
from car_logic import insurance, trip_cost


def main():

    put_markdown("# Інформація про авто")

    put_text(f"Назва авто: {car['модель']}")
    put_text(f"Ціна: {car['ціна']} грн")
    put_text(f"Обєм двигуна: {car['робочий_обєм_двигуна']} л")
    put_text(f"Повна маса: {car['повна_маса']} кг")
    put_text(f"Максимальна швидкість: {car['максимальна_швидкість']} км/год")
    put_text(f"Витрата пального: {car['витрата_пального_на_100км']} л/100 км")

    put_markdown("## Особливості інтерєру")

    for option in car["особливості_інтерєру"]:
        put_text(option)

    put_markdown("## Багажне відділення")

    put_text(
        f"Обєм багажника: "
        f"{car['параметри_багажного_відділення']['обєм_багажника']} л"
    )

    put_text(
        f"Обєм зі складеними сидіннями: "
        f"{car['параметри_багажного_відділення']['обєм_зі_складеними_сидіннями']} л"
    )

    put_markdown("## Додаткова інформація")

    put_text(
        f"Максимальна дозволена маса причепа: "
        f"{car['максимальна_дозволена_маса_причепа']} кг"
    )

    put_text(f"Страховий платіж: {insurance} грн")

    put_text(f"Вартість поїздки на 200 км: {trip_cost} грн")


start_server(main, port=8080)