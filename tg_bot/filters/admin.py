import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.filters import Filter

from tg_bot.config import Config


class AdminFilter(Filter):
    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def __call__(self, message, config: Config):
        if self.is_admin is None:
            return False
        return (message.from_user.id in config.tg_bot.admin_ids) == self.is_admin

