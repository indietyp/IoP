# from marrow.mailer import Mailer
from email.mime.text import MIMEText
import smtplib
from marrow.mailer import Message
from models.security import MailAccount
from tools.security import KeyChain


class ThisIsATest(str):
  def decode(*args):
    print('test')

  def encode(*args):
    print('test')


class NotificationMailer(object):
  """docstring for NotificationMailer"""
  def __init__(self):
    pass

  def get_notification_mailer(self):
    notification_account = MailAccount.select()\
                                      .where(MailAccount.daemon == True)[0]

    conn = smtplib.SMTP_SSL(notification_account.server)
    crypt_pwd = notification_account.password
    password = KeyChain().decrypt(crypt_pwd.secret, crypt_pwd.message)

    return conn, [notification_account, password]

  def send_message(self, mailer, author, password, to, subject, content):
    msg = MIMEText(content)
    msg['Subject'] = subject

    mailer.login(author, password)
    mailer.sendmail(author, to, msg.as_string())
    mailer.quit()
if __name__ == "__main__":
  mailer, account = NotificationMailer().get_notification_mailer()

  NotificationMailer().send_message(mailer, account[0].account, 'x97y3bY89@', 'bilalmahmoud@posteo.de', 'test', 'test')
