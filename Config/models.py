""" Jyonn Liu 180111

系统配置类
"""
from SmartDjango import models, E


@E.register(id_processor=E.idp_cls_prefix())
class ConfigError:
    CREATE_CONFIG = E("更新配置错误")
    CONFIG_NOT_FOUND = E("不存在的配置")


class Config(models.Model):
    key = models.CharField(
        max_length=255,
        unique=True,
    )
    value = models.CharField(
        max_length=255,
    )

    @classmethod
    def get_config_by_key(cls, key):
        cls.validator(locals())

        try:
            config = cls.objects.get(key=key)
        except cls.DoesNotExist as err:
            raise ConfigError.CONFIG_NOT_FOUND(debug_message=err)

        return config

    @classmethod
    def get_value_by_key(cls, key, default=None):
        try:
            config = cls.get_config_by_key(key)
            return config.value
        except Exception:
            return default

    @classmethod
    def update_value(cls, key, value):
        cls.validator(locals())

        try:
            config = cls.get_config_by_key(key)
            config.value = value
            config.save()
        except E as e:
            if e.eis(ConfigError.CONFIG_NOT_FOUND):
                try:
                    config = cls(
                        key=key,
                        value=value,
                    )
                    config.save()
                except Exception as err:
                    raise ConfigError.CREATE_CONFIG(debug_message=err)
            else:
                raise e
        except Exception as err:
            raise ConfigError.CREATE_CONFIG(debug_message=err)


class ConfigInstance:
    JWT_ENCODE_ALGO = 'JWT_ENCODE_ALGO'
    PROJECT_SECRET_KEY = 'PROJECT_SECRET_KEY'

    NOTIFICATOR_NAME = 'NOTIFICATOR_NAME'
    NOTIFICATOR_TOKEN = 'NOTIFICATOR_TOKEN'
    NOTIFICATOR_HOST = 'NOTIFICATOR_HOST'


CI = ConfigInstance
