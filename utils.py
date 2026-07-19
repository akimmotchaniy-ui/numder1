import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config
import jinja2


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')


def render_template(template_file: str, data: dict) -> str:
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATES_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_file)
    return template.render(data)


def create_string_info(data: dict) -> str:
    return render_template('string.html', data)


def send_email(
    recipients: list[str],
    mail_body: str,
    mail_subject: str,
    attachment: str = None,
):
    TOKEN = config.TOKEN_UKR_NET
    USER = config.USER_UKR_NET
    SMTP_SERVER = config.SMTP_SERVER or 'smtp.ukr.net'

    if not USER or not TOKEN:
        raise RuntimeError(
            'USER_UKR_NET або TOKEN_UKR_NET не знайдені. '
            'Перевір файл .env у корені проекту.'
        )

    msg = MIMEMultipart('alternative')
    msg['Subject'] = mail_subject
    msg['From'] = f'<Email was sent from {USER}>'
    msg['To'] = ', '.join(recipients)
    msg['Reply-To'] = USER
    msg['Return-Path'] = USER
    msg['X-Mailer'] = 'decorator'

    text_to_send = MIMEText(mail_body, 'html')
    msg.attach(text_to_send)

    if attachment:
        is_file_exists = os.path.exists(attachment)
        if is_file_exists:
            basename = os.path.basename(attachment)
            filesize = os.path.getsize(attachment)
            file = MIMEBase('application', f'octet-stream; name={basename}')
            file.set_payload(open(attachment, 'br').read())
            file.add_header('Content-Description', attachment)
            file.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment}, size={filesize}',
            )
            encoders.encode_base64(file)
            msg.attach(file)

    mail = smtplib.SMTP_SSL(SMTP_SERVER, 465)
    mail.ehlo()
    mail.login(USER, TOKEN)
    mail.sendmail(USER, recipients, msg.as_string())
    mail.quit()
