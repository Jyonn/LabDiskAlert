from SmartDjango import Analyse
from django import views

from User.models import User, UserP
from utils.auth import Auth


class UserView(views.View):
    @staticmethod
    @Auth.require_user(admin=True)
    def get(_):
        """
        获取用户列表
        GET /api/user
        """
        return User.get_all()

    @staticmethod
    @Auth.require_user(admin=True)
    @Analyse.r(b=[UserP.name])
    def post(r):
        """
        创建用户
        POST /api/user
        """
        return User.create(name=r.d.name, password=r.d.name).d()

    @staticmethod
    @Auth.require_user(root=True)
    @Analyse.r(b=[UserP.name_getter, 'as_admin'])
    def put(r):
        """
        设置或取消管理员
        PUT /api/user
        """
        return r.d.user.set_admin(r.d.as_admin).d()


class UserNameView(views.View):
    @staticmethod
    @Auth.require_user(admin=True)
    @Analyse.r(a=[UserP.name_getter])
    def get(r):
        """
        获取用户信息
        GET /api/user/:name
        """
        return r.d.user.d()

    @staticmethod
    @Analyse.r(a=[UserP.name_getter], b=[UserP.password])
    def post(r):
        """
        登录
        POST /api/user/:name
        """
        user = r.d.user.auth(r.d.password)
        return Auth.get_user_token(user)

    @staticmethod
    @Auth.require_user(admin=True)
    @Analyse.r(a=[UserP.name_getter])
    def delete(r):
        """
        删除用户
        DELETE /api/user/:name
        """
        r.d.user.remove(executor=r.user)


class UserMeView(views.View):
    @staticmethod
    @Auth.require_user()
    def get(r):
        """
        获取自己的信息
        GET /api/user/me
        """
        return r.user.d()

    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.silent])
    def post(r):
        """
        修改全局静默设置
        POST /api/user/me
        """
        return r.user.silence(silent=r.d.silent).d()

    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.password])
    def put(r):
        """
        修改密码
        PUT /api/user/me
        """
        return r.user.update_password(r.d.password).d()


class UserEmailView(views.View):
    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.email])
    def put(r):
        """
        修改邮箱
        PUT /api/user/email
        """
        return r.user.update_email(r.d.email).d()

    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.silent])
    def post(r):
        """
        修改邮箱静默设置
        POST /api/user/email
        """
        return r.user.silence_email(r.d.silent).d()


class UserEmailCaptchaView(views.View):
    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.email_captcha])
    def put(r):
        """
        验证邮箱
        POST /api/user/email/captcha
        """
        return r.user.verify_email(r.d.email_captcha).d()


class UserPhoneView(views.View):
    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.phone])
    def put(r):
        """
        修改手机
        PUT /api/user/phone
        """
        return r.user.update_phone(r.d.phone).d()

    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.silent])
    def post(r):
        """
        修改手机静默设置
        POST /api/user/phone
        """
        return r.user.silence_phone(r.d.silent).d()


class UserPhoneCaptchaView(views.View):
    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.phone_captcha])
    def put(r):
        """
        验证手机
        POST /api/user/phone/captcha
        """
        return r.user.verify_phone(r.d.phone_captcha).d()


class UserBarkView(views.View):
    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.bark])
    def put(r):
        """
        修改Bark
        PUT /api/user/bark
        """
        return r.user.update_bark(r.d.bark).d()

    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.silent])
    def post(r):
        """
        修改Bark静默设置
        POST /api/user/bark
        """
        return r.user.silence_bark(r.d.silent).d()


class UserBarkCaptchaView(views.View):
    @staticmethod
    @Auth.require_user()
    @Analyse.r(b=[UserP.bark_captcha])
    def put(r):
        """
        验证Bark
        POST /api/user/bark/captcha
        """
        return r.user.verify_bark(r.d.bark_captcha).d()
