from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.lexicon.atomy import LEXICON_RU
from tg_bot.states.atomy import FSMAtomy
from tg_bot.utils.atomy import check_user

# Инициализируем роутер уровня модуля
router = Router()


@router.message(Command('atomy'))
async def enter_atomy(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['atomy'])
    await state.set_state(FSMAtomy.fa)


@router.message(StateFilter(FSMAtomy.fa))
async def enter_im(message: Message, state: FSMContext):
    await state.update_data(LastName=message.text.strip())
    await message.answer(text=LEXICON_RU['fa'])
    await state.set_state(FSMAtomy.im)


@router.message(StateFilter(FSMAtomy.im))
async def enter_ot(message: Message, state: FSMContext):
    await state.update_data(FirstName=message.text.strip())
    await message.answer(text=LEXICON_RU['im'])
    await state.set_state(FSMAtomy.ot)


@router.message(StateFilter(FSMAtomy.ot))
async def enter_da(message: Message, state: FSMContext):
    await state.update_data(MiddleName=message.text.strip())
    await message.answer(text=LEXICON_RU['ot']+datetime.today().strftime('%d %m %Y'))
    await state.set_state(FSMAtomy.da)


@router.message(StateFilter(FSMAtomy.da))
async def enter_te(message: Message, state: FSMContext):
    date = datetime.strptime(message.text.strip(), '%d %m %Y').strftime('%Y%m%d')
    await state.update_data(BirthDay=date)
    await message.answer(text=LEXICON_RU['da'])
    await state.set_state(FSMAtomy.te)


@router.message(StateFilter(FSMAtomy.te))
async def get_data(message: Message, state: FSMContext):
    await state.update_data(HandPhone1=message.text.strip())
    data = await state.get_data()
    print(data)
    ret = await check_user(data)
    await message.answer(ret)
    await state.clear()
    await message.answer(text=LEXICON_RU['te'])
