from collections import namedtuple
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from .deps import jinjaEnv, logger, oj_db
from .lib_cfg import config

Tpl = namedtuple('Tpl', ['file', 'subject', 'variables', 'attach_pdf'])
OJ_ENV = config.key('oj_env')

TEMPLATE_CONFIG = {
    # User created new document
    'new_account': Tpl(
        'new_account.html',
        'Notif: Nouveau document / Nieuw document',
        ['fname', 'lname'],
        False
    ),
    'lost_password': Tpl(
        'lost_password.html',
        'Réinitialisation Mot de passe / Wachtwoord reset',
        ['fname', 'lname', 'token'],
        False
    ),
}


async def notify(email, templateName, data):
    try:
        tp = TEMPLATE_CONFIG[templateName]
        template = jinjaEnv.get_template(tp.file)
        body = template.render({
            **data,
            'subject': tp.subject,
            'domain': config.key('oj_domain'),
        })
        subject = tp.subject if OJ_ENV == 'prod' else f"[{OJ_ENV}] {tp.subject}"

        send_mail(email, subject, body, [])
        logger.info("notification mail \'%s\' sent", subject)
    except Exception as e:
        logger.warning("Failed to send notification type %s to %s", templateName, email)
        logger.exception(e)


def send_mail(mTo, mSubject, mBody, mAttach):
    mFrom = config.key(['smtp', 'user'])

    message = MIMEMultipart()
    message['Subject'] = mSubject
    message['From'] = "noreply@openjustice.be"
    message['To'] = mTo

    message.attach(MIMEText(mBody, "html"))

    [message.attach(m) for m in mAttach]

    msgBody = message.as_string()

    try:
        server = SMTP(host=config.key(['smtp', 'host']), port=config.key(['smtp', 'port']), timeout=5)
        # TLS Deactivated for internal mail server use
        # server.starttls()
        server.login(mFrom, config.key(['smtp', 'password']))
        server.sendmail(mFrom, mTo, msgBody)
        server.quit()
    except Exception as e:
        logger.critical("Failed to send a message")
        logger.exception(e)
