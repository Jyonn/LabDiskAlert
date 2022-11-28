from SmartDjango import NetPacker

from Config.models import Config, CI

import ssl

from utils.safe_notificator import SafeNotificator

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


class Global:
    SECRET_KEY = Config.get_value_by_key(CI.PROJECT_SECRET_KEY)
    JWT_ENCODE_ALGO = Config.get_value_by_key(CI.JWT_ENCODE_ALGO)

    NOTIFICATOR_NAME = Config.get_value_by_key(CI.NOTIFICATOR_NAME)
    NOTIFICATOR_TOKEN = Config.get_value_by_key(CI.NOTIFICATOR_TOKEN)
    NOTIFICATOR_HOST = Config.get_value_by_key(CI.NOTIFICATOR_HOST)

    notificator = SafeNotificator(
        name=NOTIFICATOR_NAME,
        token=NOTIFICATOR_TOKEN,
        host=NOTIFICATOR_HOST,
    )


NetPacker.set_mode(debug=True)

