import utils


def main():
    utils.send_email(
        recipients=['test_hillel_api_mailing@ukr.net', 'awa123awa@ukr.net'],
        mail_body='this is mail body <br> another line',
        mail_subject='Test data',
        attachment='2026-04-03_20-10.png'
    )


main()