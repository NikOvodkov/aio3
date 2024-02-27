import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from autorun import return_bot_status, print_telegram
from tg_bot.config import load_config, Config
from tg_bot.daemons.life_calendar import send_life_calendar

from tg_bot.database.sqlite import SQLiteDatabase
from tg_bot.handlers import a_user, a_other, a_admin, atomy, gsheet, life_calendar
from tg_bot.services.setting_commands import force_reset_all_commands, set_default_commands, set_admins_commands, set_all_groups_commands, set_all_chat_admins_commands, set_all_private_commands
from aiogram.fsm.storage.redis import RedisStorage, Redis

logger = logging.getLogger(__name__)


async def set_all_default_commands(bot: Bot, config: Config):
    await force_reset_all_commands(bot)
    await set_default_commands(bot)
    await set_admins_commands(bot, config.tg_bot.admin_ids[0])
    await set_all_groups_commands(bot)
    await set_all_chat_admins_commands(bot)
    await set_all_private_commands(bot)


async def on_startup_notify(bot: Bot, config: Config):
    for admin in config.tg_bot.admin_ids:
        try:
            await bot.send_message(admin, "Бот Запущен и готов к работе")
        except Exception as err:
            logging.exception(err)


async def daemons(bot, db, dp):
    await send_life_calendar(db, bot, dp)


async def writelog(dp: Dispatcher):
    while True:
        await asyncio.sleep(30)
        logging.info('Bot is working.')
        dp['autorun_was_working'] = dp['autorun_is_working']
        dp['autorun_is_working'] = return_bot_status('autorun.txt', 120)
        if dp['autorun_is_working'] != dp['autorun_was_working']:
            if dp['autorun_is_working']:
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
        return RedisStorage(redis=Redis(host='localhost'))
    else:
        return MemoryStorage()


async def main():
    logging.basicConfig(level=logging.INFO, #filename='bot.log',
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s -%(message)s')
    config = load_config('.env')
    storage = get_storage(config)
    dp = Dispatcher(storage=storage)
    dp['config'] = config
    db = SQLiteDatabase()
    dp['db'] = db

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

    dp.include_routers(a_admin.router,
                       a_user.router,
                       atomy.router,
                       gsheet.router,
                       life_calendar.router,
                       a_other.router)

    await set_all_default_commands(bot, config)
    await on_startup_notify(bot, config)

    task1 = asyncio.create_task(dp.start_polling(bot))
    task2 = asyncio.create_task(writelog(dp=dp))
    task3 = asyncio.create_task(daemons(bot=bot, db=db, dp=dp))

    await task1
    await task2
    await task3


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')
