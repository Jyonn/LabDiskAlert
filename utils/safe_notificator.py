from typing import Optional

from CentralNotificationSDK import Notificator
from SmartDjango import E


@E.register(id_processor=E.idp_cls_prefix())
class NotificatorError:
    SEND_ERROR = E("发送通知失败")


class SafeNotificator:
    def __init__(self, name, token, host):
        self.notificator = Notificator(
            name=name,
            token=token,
            host=host,
        )

    def sms(
            self,
            phone,
            content,
    ):
        try:
            self.notificator.sms(phone, content)
        except Exception as e:
            raise NotificatorError.SEND_ERROR(debug_message=e)

    def sms_captcha(
            self,
            phone,
            captcha,
            name,
    ):
        self.sms(
            phone=phone,
            content=f'Hi {name}, the captcha is {captcha}'
        )

    def mail(
            self,
            mail: str,
            content: str,
            subject: Optional[str] = None,
            appellation: Optional[str] = None,
    ):
        try:
            self.notificator.mail(mail, content, subject, appellation)
        except Exception as e:
            raise NotificatorError.SEND_ERROR(debug_message=e)

    def mail_captcha(
            self,
            mail: str,
            captcha: str,
            name: str,
    ):
        self.mail(
            mail=mail,
            content=f'The captcha is {captcha}',
            appellation=name,
        )

    def bark(
            self,
            uri: str,
            content: str,
            title: Optional[str] = None,
            sound: Optional[str] = None,
            icon: Optional[str] = None,
            group: Optional[str] = None,
            url: Optional[str] = None,
    ):
        try:
            self.notificator.bark(
                uri=uri,
                content=content,
                title=title,
                sound=sound,
                icon=icon,
                group=group,
                url=url
            )
        except Exception as e:
            raise NotificatorError.SEND_ERROR(debug_message=e)

    def bark_captcha(
            self,
            uri: str,
            captcha: str,
            name: str,
    ):
        self.bark(
            uri=uri,
            content=f'Hi {name}, the captcha is {captcha}',
            title='Captcha Notice',
        )
