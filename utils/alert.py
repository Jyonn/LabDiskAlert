from SmartDjango import E

from Host.models import DiskUser
from LabDiskAlert.global_settings import Global


def alert(diskuser: DiskUser, message, title):
    user = diskuser.user
    if user.silent:
        return False

    alert_flag = False
    fail_log = []
    if user.phone_activated and not user.phone_silent:
        try:
            Global.notificator.sms(user.phone, message)
            alert_flag = True
        except E as e:
            fail_log.append(e.debug_message)

    if user.email_activated and not user.email_silent:
        try:
            Global.notificator.mail(user.email, message, subject=title, appellation=user.name)
            alert_flag = True
        except E as e:
            fail_log.append(e.debug_message)

    if user.bark_activated and not user.bark_silent:
        try:
            Global.notificator.bark(user.bark, message, title=title)
            alert_flag = True
        except E as e:
            fail_log.append(e.debug_message)

    return alert_flag, fail_log
