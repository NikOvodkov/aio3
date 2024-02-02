import asyncio
import logging
import time

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder

from autorun import return_bot_status, print_telegram
from tg_bot.config import load_config, Config
from tg_bot.daemons.life_calendar import send_life_calendar
from tg_bot.db.sqlite import SQLiteDatabase
from tg_bot.filters.admin import AdminFilter
from tg_bot.handlers.admin import register_admin, admin_router
from tg_bot.handlers.atomy import register_atomy
from tg_bot.handlers.echo import register_echo, echo_router
from tg_bot.handlers.group_approval import register_group_approval
from tg_bot.handlers.help import register_help, help_router
from tg_bot.handlers.life_calendar import register_life_calendar
from tg_bot.handlers.test_location import register_test_location
from tg_bot.handlers.update_db_sqlite import register_update_db_sqlite
from tg_bot.handlers.user import register_user
from tg_bot.middlewares.db import DbMiddleware
from tg_bot.middlewares.throttling import ThrottlingMiddleware
from tg_bot.services.setting_commands import force_reset_all_commands, set_default_commands, set_admins_commands, set_all_groups_commands, set_all_chat_admins_commands, set_all_private_commands

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    dp.setup_middleware(ThrottlingMiddleware())
    dp.setup_middleware(DbMiddleware(config=dp['config'], db=dp['db']))


async def set_all_default_commands(bot: Bot, config: Config):
    await force_reset_all_commands(bot)
    await set_default_commands(bot)
    await set_admins_commands(bot, config.tg_bot.admin_ids[0])
    await set_all_groups_commands(bot)
    await set_all_chat_admins_commands(bot)
    await set_all_private_commands(bot)


async def on_startup_notify(dp: Dispatcher, config: Config):
    for admin in config.tg_bot.admin_ids:
        try:
            await dp.bot.send_message(admin, "Бот Запущен и готов к работе")
        except Exception as err:
            logging.exception(err)


async def daemons(bot, db, dp):
    await send_life_calendar(db, bot, dp)


async def writelog(bot: Bot):
    while True:
        await asyncio.sleep(30)
        logging.info('Bot is working.')
        bot['autorun_was_working'] = bot['autorun_is_working']
        bot['autorun_is_working'] = return_bot_status('autorun.txt', 120)
        if bot['autorun_is_working'] != bot['autorun_was_working']:
            if bot['autorun_is_working']:
                print('\r', 'Nib: autorun zarabotal', end='')
                await print_telegram('Nib: autorun zarabotal')
            else:
                print('\r', 'Nib: autorun ostanovilsya', end='')
                await print_telegram('Nib: autorun ostanovilsya')


def get_storage(config):
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main():
    logging.basicConfig(level=logging.INFO, filename='bot.log',
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s -%(message)s')
    config = load_config('.env')
    storage = get_storage(config)
    dp = Dispatcher(storage=storage)
    dp['config'] = config
    db = SQLiteDatabase()
    dp['db'] = db
    # dp.workflow_data.update(config=config) # то же что и dp['config'] = config

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

    if return_bot_status('autorun.txt', 120):
        print('\r', 'Nib: autorun rabotaet', end='')
        await print_telegram('Nib: autorun rabotaet')
        dp['autorun_is_working'] = True
    else:
        print('\r', 'Nib: autorun ne rabotaet', end='')
        await print_telegram('Nib: autorun ne rabotaet')
        dp['autorun_is_working'] = False




    try:
        logging.info('Создаём подключение к базе данных')
        db.create_table_users()
    except Exception as e:
        print(e)
    # logging.info('Чистим базу')
    # db.delete_users()
    print(db.select_all_users())

    register_all_middlewares(dp)
    dp.include_routers(admin_router, help_router, echo_router)

    await set_all_default_commands(bot, config)
    await on_startup_notify(dp, config)

    task1 = asyncio.create_task(dp.start_polling(bot))
    task2 = asyncio.create_task(writelog(bot=bot))
    task3 = asyncio.create_task(daemons(bot=bot, db=db, dp=dp))

    await task1
    await task2
    await task3


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')
