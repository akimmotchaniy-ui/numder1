import re

from pywebio.input import TEXT, input, input_group
from pywebio.output import put_text

import utils

EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$')


def validate_email(value: str) -> str | None:
    if not EMAIL_PATTERN.match(value.strip()):
        return 'Введіть коректну електронну пошту'
    return None


def validate_not_empty(value: str) -> str | None:
    if not value.strip():
        return 'Поле не може бути порожнім'
    return None


def get_user_data() -> dict:
    return input_group(
        'Обчислення довжини стрічки',
        [
            input('Ваше імʼя', name='name', type=TEXT, required=True, validate=validate_not_empty),
            input('Стрічка', name='line', type=TEXT, required=True, validate=validate_not_empty),
            input('Електронна пошта', name='email', type=TEXT, required=True, validate=validate_email),
        ],
    )


def prepare_context(user_data: dict) -> dict:
    line = user_data['line'].strip()
    return {
        'name': user_data['name'].strip(),
        'email': user_data['email'].strip(),
        'line': line,
        'length': len(line),
    }


def main():
    context = prepare_context(get_user_data())
    mail_body = utils.create_string_info(context)

    utils.send_email(
        recipients=[context['email']],
        mail_body=mail_body,
        mail_subject=f'Довжина стрічки - {context["length"]} символів',
    )

    put_text(f'Лист надіслано на {context["email"]}. Довжина стрічки: {context["length"]}')


main()
