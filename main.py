import utils


def main():
    trip_data = {
        'name': 'Akim',
        'date': '05.06.2026',
        'persons': 6,
        'price_per_person': 6000054,
        'total_price': 6000,
        'discount': 0,
        'final_price': 6000
    }
    mail_body = utils.create_trip_info(trip_data)
    print(mail_body)

    utils.send_email(
        recipients=['test_hillel_api_mailing@ukr.net', 'awa123awa@ukr.net'],
        mail_body=mail_body,
        mail_subject=f'Trip data - total={trip_data["final_price"]}',
        # attachment='2026-04-03_20-10.png'
    )


main()