import sqlite3

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter

from tg_bot.config import Config
from tg_bot.database.sqlite import SQLiteDatabase
from tg_bot.lexicon.a_user import LEXICON_RU
from tg_bot.services.setting_commands import set_starting_commands
from tg_bot.states.user import FSMUser

# Инициализируем роутер уровня модуля
router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message, db: SQLiteDatabase, state: FSMContext, config: Config):
    await state.clear()
    await set_starting_commands(message.bot, message.from_user.id)
    name = message.from_user.full_name
    try:
        db.add_user(user_id=message.from_user.id, name=name)
        await message.forward(config.tg_bot.admin_ids[0])
    except sqlite3.IntegrityError as err:
        print(err)
    await message.answer(text=LEXICON_RU['/start'])


# Этот хэндлер срабатывает на команду /about
@router.message(Command(commands='about'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/about'])


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['/help'])
    await state.set_state(FSMUser.user_help)


@router.message(StateFilter(FSMUser.user_help))
async def enter_message(message: Message, state: FSMContext, config: Config):
    await message.forward(config.tg_bot.admin_ids[0])
    await message.answer(text=LEXICON_RU['help'])
    await state.clear()



