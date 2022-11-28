from functools import wraps

from SmartDjango import E

from Host.models import Host
from User.models import User
from utils.jtoken import JWT


@E.register()
class AuthError:
    REQUIRE_LOGIN = E("需要登录")
    REQUIRE_ROOT = E("需要根用户登录")
    REQUIRE_ADMIN = E("需要管理员登录")

    FAIL_AUTH = E("登录失败")
    TOKEN_MISS_PARAM = E('认证口令缺少参数"{0}"')


class AuthType:
    USER = 0
    DISK = 1


class Auth:
    @staticmethod
    def validate_token(r):
        jwt_str = r.META.get('HTTP_TOKEN')
        if jwt_str is None:
            raise AuthError.REQUIRE_LOGIN
        return JWT.decrypt(jwt_str)

    @staticmethod
    def get_user_token(user):
        token, d = JWT.encrypt(dict(name=user.name, type=AuthType.USER))
        d['token'] = token
        d['user'] = user.d()
        return d

    @staticmethod
    def get_host_token(host):
        token, d = JWT.encrypt(dict(name=host.name, type=AuthType.DISK))
        d['token'] = token
        d['host'] = host.d()
        return d

    @classmethod
    def _extract_user(cls, r):
        r.user = None

        d = Auth.validate_token(r)

        name = d.get('name')
        if name is None:
            raise AuthError.TOKEN_MISS_PARAM('name')

        type_ = d.get('type')
        if type_ is None:
            raise AuthError.TOKEN_MISS_PARAM('type')

        if type_ != AuthType.USER:
            raise AuthError.FAIL_AUTH

        r.user = User.get_user_by_name(name)

    @classmethod
    def _extract_host(cls, r):
        r.host = None

        d = Auth.validate_token(r)
        name = d.get('name')
        if name is None:
            raise AuthError.TOKEN_MISS_PARAM('name')

        type_ = d.get('type')
        if type_ is None:
            raise AuthError.TOKEN_MISS_PARAM('type')

        if type_ != AuthType.DISK:
            raise AuthError.FAIL_AUTH

        r.host = Host.get_host_by_name(name)

    @classmethod
    def require_user(
            cls,
            root=False,
            admin=False,
    ):
        def decorator(func):
            @wraps(func)
            def wrapper(r, *args, **kwargs):
                try:
                    cls._extract_user(r)
                except Exception as err:
                    raise AuthError.REQUIRE_LOGIN(debug_message=err)

                if root:
                    if not r.user.is_root:
                        raise AuthError.REQUIRE_ROOT

                if admin:
                    if not r.user.is_admin:
                        raise AuthError.REQUIRE_ADMIN

                return func(r, *args, **kwargs)
            return wrapper
        return decorator

    @classmethod
    def require_host(cls):
        def decorator(func):
            @wraps(func)
            def wrapper(r, *args, **kwargs):
                try:
                    cls._extract_host(r)
                except Exception as err:
                    raise AuthError.REQUIRE_LOGIN(debug_message=err)

                return func(r, *args, **kwargs)
            return wrapper
        return decorator
