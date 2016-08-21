from marrow.mailer import Mailer
from marrow.mailer import Message
from models.security import MailAccount
from tools.security import KeyChain


class NotificationMailer(object):
  """docstring for NotificationMailer"""
  def __init__(self):
    pass

  def get_notification_mailer(self):
    notification_account = MailAccount.select()\
                                       .where(MailAccount.daemon == True)[0]

    crypt_pwd = notification_account.password
    password = KeyChain().decrypt(crypt_pwd.secret, crypt_pwd.message)

    mailer = Mailer({
        'transport.use': notification_account.transport,
        'transport.host': notification_account.server,
        'transport.port': notification_account.port,
        'transport.tls': notification_account.encryption,
        'transport.username': notification_account.account,
        'transport.password': password,
        'manager': {}})

    return mailer, notification_account

  def send_message(self, mailer, author, to, subject, content):
    mailer.start()
    message = Message()
    message.to = to
    message.subject = subject
    message.plain = content
    mailer.send(message)
    mailer.stop()

if __name__ == "__main__":
  NotificationMailer().get_notification_mailer()
