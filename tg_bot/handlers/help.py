from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.config import Config
from tg_bot.db.sqlite import SQLiteDatabase
from tg_bot.handlers.user import user_start
from tg_bot.misc.throttling import rate_limit


help_router = Router()


@rate_limit(3)
@help_router.message(Command('about'))
async def enter_about(message: Message, state: FSMContext, bot: Bot):
    await message.answer('Календарь жизни - это таблица с кружкАми, из которой визуально понятно какая часть жизни '
                         'уже прожита. 1 кружок равен 1 неделе жизни. '
                         'Если вам нужна дополнительная мотивация, можете подписаться '
                         'на еженедельную рассылку календаря и наблюдать, как количество кружков медленно уменьшается. '
                         'Если от этих рассылок вам станет грустно, то всегда можно отписаться. Или можно поделиться '
                         'с другом ссылкой на бота, пусть он тоже погрустит. Вместе грустить веселее. 😊')
    await state.clear()


@rate_limit(3)
@help_router.message(Command('help'))
async def enter_help(message: Message, state: FSMContext, bot: Bot):
    await message.answer('Здравствуйте! Бот может работать с небольшой задержкой.\n'
                         'Если бот не отвечает на команды более 10 секунд, или наблюдается другая проблема,'
                         ' или у вас есть предложение по совершенствованию бота, вы можете написать автору'
                         ' в ответ на данное сообщение.')
    await state.set_state('help')


@rate_limit(3)
@help_router.message(StateFilter('help'))
async def enter_message(message: Message, state: FSMContext, config: Config, bot: Bot):
    await message.forward(config.tg_bot.admin_ids[0])
    await message.answer('Ваше обращение принято. Чтобы отправить ещё одно обращение, '
                         'необходимо повторно ввести\nкоманду /help.')
    await state.clear()
