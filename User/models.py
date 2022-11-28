import random
import re
import string

from SmartDjango import models, E
from SmartDjango.models import CREnum
from SmartDjango.p import P
from django.utils.crypto import get_random_string

from LabDiskAlert.global_settings import Global
from utils.hash import md5


@E.register(id_processor=E.idp_cls_prefix())
class UserError:
    NAME_NOT_FOUND = E("用户名不存在")
    EMAIL_NOT_FOUND = E("邮箱不存在")
    INVALID_NAME = E("用户名不合法，只能包含字母、数字、下划线")
    INVALID_PASSWORD = E("密码不合法，{0}")
    INVALID_EMAIL = E("邮箱不合法")
    PASSWORD_ERROR = E("密码错误")
    INVALID_BARK = E("Bark链接不合法")

    NAME_EXISTS = E("用户名已存在")

    CANNOT_DELETE_ROOT = E("不能删除根用户")
    CANNOT_DELETE_SELF = E("不能删除自己")
    CANNOT_DELETE_ADMIN = E("不能删除管理员")

    PHONE_NOT_ACTIVATED = E("手机号未激活")
    EMAIL_NOT_ACTIVATED = E("邮箱未激活")
    EMAIL_TEMPORARILY_UNAVAILABLE = E("邮箱暂时不可用")
    BARK_NOT_ACTIVATED = E("Bark未激活")

    PHONE_ALREADY_ACTIVATED = E("手机号已激活")
    EMAIL_ALREADY_ACTIVATED = E("邮箱已激活")
    BARK_ALREADY_ACTIVATED = E("Bark已激活")

    BIND_PHONE_FIRST = E("请先绑定手机号")
    BIND_EMAIL_FIRST = E("请先绑定邮箱")
    BIND_BARK_FIRST = E("请先绑定Bark")

    CAPTCHA_ERROR = E("验证码错误")


class ChannelStatus(CREnum):
    WAIT_BIND = 0
    WAIT_CAPTCHA = 1
    ACTIVATED = 2


class User(models.Model):
    ROOT_ID = 1

    name = models.CharField(
        min_length=3,
        max_length=10,
        unique=True,
    )

    password = models.CharField(
        min_length=6,
        max_length=32,
    )

    admin = models.BooleanField(
        default=False,
    )

    salt = models.CharField(
        max_length=6,
    )

    silent = models.BooleanField(
        default=False,
    )

    email = models.EmailField(
        max_length=30,
        null=True,
        blank=True,
    )

    email_captcha = models.CharField(
        max_length=6,
        null=True,
        blank=True,
    )

    email_status = models.IntegerField(
        choices=ChannelStatus.list(),
        default=ChannelStatus.WAIT_BIND.value,
    )

    email_silent = models.BooleanField(
        default=False,
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    phone_captcha = models.CharField(
        max_length=6,
        null=True,
        blank=True,
    )

    phone_status = models.IntegerField(
        choices=ChannelStatus.list(),
        default=ChannelStatus.WAIT_BIND.value,
    )

    phone_silent = models.BooleanField(
        default=False,
    )

    bark = models.CharField(
        max_length=64,
        null=True,
        blank=True,
    )

    bark_captcha = models.CharField(
        max_length=6,
        null=True,
        blank=True,
    )

    bark_status = models.IntegerField(
        choices=ChannelStatus.list(),
        default=ChannelStatus.WAIT_BIND.value,
    )

    bark_silent = models.BooleanField(
        default=False,
    )

    @staticmethod
    def _valid_name(name):
        """验证账户名合法"""
        valid_chars = '^[A-Za-z0-9_]*$'
        if re.match(valid_chars, name) is None:
            raise UserError.INVALID_NAME

    @staticmethod
    def _valid_password(password):
        valid_chars = string.digits + string.ascii_letters + string.punctuation
        for char in password:
            if char not in valid_chars:
                raise UserError.INVALID_PASSWORD(message=f'非法字符"{char}"')

    @staticmethod
    def _valid_email(email):
        if not re.match(r'^[.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            raise UserError.INVALID_EMAIL

    @staticmethod
    def _valid_bark(bark):
        if not re.match(r'^https://api.day.app/[a-zA-Z0-9]+/?$', bark):
            raise UserError.INVALID_BARK

    @classmethod
    def get_user_by_name(cls, name):
        try:
            user = cls.objects.get(name=name)
        except cls.DoesNotExist as err:
            raise UserError.NAME_NOT_FOUND(debug_message=err)
        return user

    @classmethod
    def name_exists(cls, name):
        return cls.objects.filter(name=name).exists()

    @classmethod
    def generate_salt(cls):
        return get_random_string(6)

    @classmethod
    def encrypt_password(cls, password, salt=None):
        salt_ = salt or cls.generate_salt()
        password = md5(f'{password}${salt_}')
        if salt is None:
            return password, salt_
        return password

    @classmethod
    def create(cls, name, password):
        if cls.name_exists(name):
            raise UserError.NAME_EXISTS
        password, salt = cls.encrypt_password(password)
        return cls.objects.create(
            name=name,
            password=password,
            salt=salt,
            admin=False,
            email=None,
            email_silent=True,
            phone=None,
            phone_silent=True,
            bark=None,
            bark_silent=True,
            silent=False,
        )

    def auth(self, password):
        if self.password != self.encrypt_password(password, self.salt):
            raise UserError.PASSWORD_ERROR
        return self

    @property
    def phone_activated(self):
        return self.phone_status == ChannelStatus.ACTIVATED.value

    @property
    def phone_wait_bind(self):
        return self.phone_status == ChannelStatus.WAIT_BIND.value

    @property
    def phone_wait_captcha(self):
        return self.phone_status == ChannelStatus.WAIT_CAPTCHA.value

    @property
    def email_activated(self):
        return self.email_status == ChannelStatus.ACTIVATED.value

    @property
    def email_wait_bind(self):
        return self.email_status == ChannelStatus.WAIT_BIND.value

    @property
    def email_wait_captcha(self):
        return self.email_status == ChannelStatus.WAIT_CAPTCHA.value

    @property
    def bark_activated(self):
        return self.bark_status == ChannelStatus.ACTIVATED.value

    @property
    def bark_wait_bind(self):
        return self.bark_status == ChannelStatus.WAIT_BIND.value

    @property
    def bark_wait_captcha(self):
        return self.bark_status == ChannelStatus.WAIT_CAPTCHA.value

    @staticmethod
    def generate_captcha(length=6):
        return ''.join([random.choice(string.digits) for _ in range(length)])

    def silence_phone(self, silent):
        if not self.phone_activated:
            raise UserError.PHONE_NOT_ACTIVATED
        self.phone_silent = silent
        self.save()

    def update_phone(self, phone):
        self.phone = phone
        self.phone_status = ChannelStatus.WAIT_CAPTCHA.value
        self.phone_captcha = self.generate_captcha()
        self.phone_silent = False
        Global.notificator.sms_captcha(phone, self.phone_captcha, self.name)
        self.save()
        return self

    def verify_phone(self, captcha):
        if self.phone_activated:
            raise UserError.PHONE_ALREADY_ACTIVATED
        if self.phone_wait_bind:
            raise UserError.BIND_PHONE_FIRST
        if self.phone_captcha != captcha:
            raise UserError.CAPTCHA_ERROR
        self.phone_status = ChannelStatus.ACTIVATED.value
        self.save()
        return self

    def silence_email(self, silent):
        if not self.email_activated:
            raise UserError.EMAIL_NOT_ACTIVATED
        self.email_silent = silent
        self.save()
        return self

    def update_email(self, email):
        # raise UserError.EMAIL_TEMPORARILY_UNAVAILABLE
        self.email = email
        self.email_status = ChannelStatus.WAIT_CAPTCHA.value
        self.email_captcha = self.generate_captcha()
        self.email_silent = True
        Global.notificator.mail_captcha(email, self.email_captcha, self.name)
        self.save()
        return self

    def verify_email(self, captcha):
        if self.email_activated:
            raise UserError.EMAIL_ALREADY_ACTIVATED
        if self.email_wait_bind:
            raise UserError.BIND_EMAIL_FIRST
        if self.email_captcha != captcha:
            raise UserError.CAPTCHA_ERROR
        self.email_status = ChannelStatus.ACTIVATED.value
        self.save()
        return self

    def silence_bark(self, silent):
        if not self.bark_activated:
            raise UserError.BARK_NOT_ACTIVATED
        self.bark_silent = silent
        self.save()
        return self

    def update_bark(self, bark):
        self.bark = bark
        self.bark_status = ChannelStatus.WAIT_CAPTCHA.value
        self.bark_captcha = self.generate_captcha()
        self.bark_silent = True
        Global.notificator.bark_captcha(bark, self.bark_captcha, self.name)
        self.save()
        return self

    def verify_bark(self, captcha):
        if self.bark_activated:
            raise UserError.BARK_ALREADY_ACTIVATED
        if self.bark_wait_bind:
            raise UserError.BIND_BARK_FIRST
        if self.bark_captcha != captcha:
            raise UserError.CAPTCHA_ERROR
        self.bark_status = ChannelStatus.ACTIVATED.value
        self.save()
        return self

    def silence(self, silent):
        self.silent = silent
        self.save()
        return self

    def update_password(self, password):
        self.password, self.salt = self.encrypt_password(password)
        self.save()
        return self

    def d(self):
        return self.dictify(
            'name', 'admin', 'root', 'email', 'phone', 'bark', 'silent',
            'email_silent', 'phone_silent', 'bark_silent',
            'email_status', 'phone_status', 'bark_status',
        )

    def _readable_root(self):
        return self.is_root

    @property
    def is_root(self):
        return self.id == self.ROOT_ID

    @property
    def is_admin(self):
        return self.admin or self.is_root

    @classmethod
    def get_all(cls):
        return cls.objects.all().dict(cls.d)

    @classmethod
    def get_admins(cls):
        return cls.objects.filter(admin=True)

    def remove(self, executor: 'User'):
        if self.is_root:
            raise UserError.CANNOT_DELETE_ROOT
        if self.id == executor.id:
            raise UserError.CANNOT_DELETE_SELF
        if self.is_admin and not executor.is_root:
            raise UserError.CANNOT_DELETE_ADMIN
        self.delete()

    def set_admin(self, as_admin: bool):
        self.admin = as_admin
        self.save()
        return self


class UserP:
    name, password, email, phone, bark = User.P('name', 'password', 'email', 'phone', 'bark')
    phone_captcha, email_captcha, bark_captcha = User.P('phone_captcha', 'email_captcha', 'bark_captcha')

    name_getter = name.clone().rename('name', yield_name='user').process(User.get_user_by_name)
    silent = P('silent').process(bool)
