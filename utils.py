from email.mime.text import MIMEText
import email.utils
import smtplib

FROM_EMAIL = "tfi@ev3hub.com"
FROM_NAME = "TFI CheckMeIn"


def sendEmail(toName, toEmail, subject, message):
    msg = MIMEText(message)
    msg['To'] = email.utils.formataddr((toName, toEmail))
    msg['From'] = email.utils.formataddr((FROM_NAME, FROM_EMAIL))
    msg['Subject'] = subject

    try:  # pragma: no cover
        server = smtplib.SMTP('localhost')
        server.sendmail(FROM_EMAIL, [toEmail], msg.as_string())
        server.quit()
    except IOError:
        print('Email would have been:', msg)
