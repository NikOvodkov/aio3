import os
from datetime import timedelta, datetime
from pathlib import Path
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile

from tg_bot.database.sqlite import SQLiteDatabase
from tg_bot.keyboards.life_calendar import yesno, geono
from tg_bot.lexicon.life_calendar import LEXICON_RU
from tg_bot.utils.life_calendar import generate_image_calendar
from tg_bot.states.life_calendar import FSMLifeCalendar

# Инициализируем роутер уровня модуля
router = Router()


@router.message(Command(commands='life_calendar'))
async def start_life_calendar(message: Message, state: FSMContext, db: SQLiteDatabase):
    await message.answer(text=LEXICON_RU['life_calendar_0'])
    user = db.select_user(user_id=message.from_user.id)
    if user[4]:
        date = datetime.strptime(user[4], '%Y-%m-%d').strftime('%d-%m-%Y')
        await message.answer(f'{LEXICON_RU["life_calendar_1"]}{date}{LEXICON_RU["life_calendar_2"]}', reply_markup=yesno)
        await state.set_state(FSMLifeCalendar.confirm_date)
    else:
        await message.answer(text=LEXICON_RU['life_calendar_3'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMLifeCalendar.enter_date)


@router.message(StateFilter(FSMLifeCalendar.confirm_date))
async def confirm_date(message: Message, state: FSMContext):
    if message.text.lower().strip() == 'да':
        await message.answer(text=LEXICON_RU['confirm_date_0'], reply_markup=yesno)
        await state.set_state(FSMLifeCalendar.no_enter_date)
    else:
        await message.answer(text=LEXICON_RU['confirm_date_1'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMLifeCalendar.enter_date)


@router.message(StateFilter(FSMLifeCalendar.no_enter_date))
async def no_enter_date(message: Message, state: FSMContext, db: SQLiteDatabase):
    if message.text.lower().strip() == 'да':
        user = db.select_user(user_id=message.from_user.id)
        path = str(Path.cwd() / Path('tg_bot', 'utils', f'{datetime.now().strftime("%Y%m%d%H%M%S%f")}.gif'))
        await generate_image_calendar(user[4], user[5], 'week', path)
        await message.answer_photo(photo=FSInputFile(path), reply_markup=ReplyKeyboardRemove())
        os.remove(path)
        if user[6]:
            await state.clear()
        else:
            if user[3]:
                await state.set_state(FSMLifeCalendar.confirm_geo)
                await message.answer(text=LEXICON_RU['no_enter_date_0'], reply_markup=yesno)
            else:
                await state.set_state(FSMLifeCalendar.everyweek_order)
                await message.answer(text=LEXICON_RU['no_enter_date_1'], reply_markup=geono)
    else:
        await state.clear()


@router.message(StateFilter(FSMLifeCalendar.enter_date))
async def enter_date(message: Message, state: FSMContext, db: SQLiteDatabase):
    user = db.select_user(user_id=message.from_user.id)
    date = '-'.join(message.text.split())
    date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
    db.update_birth_date(birth_date=date, user_id=message.from_user.id)
    age_days = (datetime.now() - datetime.fromisoformat(date)).days
    if age_days > 21700:
        life_date = (timedelta(weeks=520) + datetime.now()).strftime('%Y-%m-%d')
        db.update_life_date(life_date=life_date, user_id=message.from_user.id)
        await message.answer(text=LEXICON_RU['enter_date_0'])
        await state.set_state(FSMLifeCalendar.oldster_enter_date)
    else:
        life_date = (timedelta(weeks=3652) + datetime.fromisoformat(date)).strftime('%Y-%m-%d')
        db.update_life_date(life_date=life_date, user_id=message.from_user.id)
        path = str(Path.cwd() / Path('tg_bot', 'utils', f'{datetime.now().strftime("%Y%m%d%H%M%S%f")}.gif'))
        await generate_image_calendar(date, life_date, 'week', path)
        await message.answer_photo(photo=FSInputFile(path), reply_markup=ReplyKeyboardRemove())
        os.remove(path)
        if user[6]:
            await state.clear()
        else:
            if user[3]:
                await state.set_state(FSMLifeCalendar.confirm_geo)
                await message.answer(text=LEXICON_RU['enter_date_1'], reply_markup=yesno)
            else:
                await state.set_state(FSMLifeCalendar.everyweek_order)
                await message.answer(text=LEXICON_RU['enter_date_2'], reply_markup=geono)


@router.message(StateFilter(FSMLifeCalendar.oldster_enter_date))
async def oldster_enter_date(message: Message, state: FSMContext, db: SQLiteDatabase):
    user = db.select_user(user_id=message.from_user.id)
    date = user[4]
    if message.text > '0':
        life_date = (timedelta(weeks=int(message.text) * 52.1786) + datetime.now()).strftime('%Y-%m-%d')
        db.update_life_date(life_date=life_date, user_id=message.from_user.id)
        path = str(Path.cwd() / Path('tg_bot', 'utils', f'{datetime.now().strftime("%Y%m%d%H%M%S%f")}.gif'))
        await generate_image_calendar(date, life_date, 'week', path)
        await message.answer_photo(photo=FSInputFile(path), reply_markup=ReplyKeyboardRemove())
        os.remove(path)
        if user[6]:
            await state.clear()
        else:
            if user[3]:
                await state.set_state(FSMLifeCalendar.confirm_geo)
                await message.answer(text=LEXICON_RU['oldster_enter_date_0'], reply_markup=yesno)
            else:
                await state.set_state(FSMLifeCalendar.everyweek_order)
                await message.answer(text=LEXICON_RU['oldster_enter_date_1'], reply_markup=geono)

    else:
        await state.clear()
        await message.answer(text=LEXICON_RU['oldster_enter_date_2'], reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(FSMLifeCalendar.confirm_geo))
async def confirm_geo(message: Message, state: FSMContext, db: SQLiteDatabase):
    if message.text.lower().strip() == 'да':
        user = db.select_user(user_id=message.from_user.id)
        await state.set_state(FSMLifeCalendar.confirm_geo_process)
        await message.answer(text=f'{LEXICON_RU["confirm_geo_0"]}{user[3]}{LEXICON_RU["confirm_geo_1"]}', reply_markup=yesno)
    else:
        db.update_life_calendar(life_calendar=None, user_id=message.from_user.id)
        await message.answer(text=LEXICON_RU["confirm_geo_2"], reply_markup=ReplyKeyboardRemove())
        await state.clear()


@router.message(StateFilter(FSMLifeCalendar.confirm_geo_process))
async def confirm_geo_process(message: Message, state: FSMContext, db: SQLiteDatabase):
    if message.text.lower().strip() == 'да':
        db.update_life_calendar(life_calendar=datetime.now().strftime('%Y-%m-%d'), user_id=message.from_user.id)
        await message.answer(text=LEXICON_RU['confirm_geo_process_0'], reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer(text=LEXICON_RU['confirm_geo_process_1'], reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMLifeCalendar.change_timezone)


@router.message(StateFilter(FSMLifeCalendar.change_timezone))
async def change_timezone(message: Message, state: FSMContext, db: SQLiteDatabase):
    time_zone = int(message.text)
    db.update_time_zone(time_zone=str(time_zone), user_id=message.from_user.id)
    db.update_life_calendar(life_calendar=datetime.now().strftime('%Y-%m-%d'), user_id=message.from_user.id)
    await message.answer(text=LEXICON_RU['change_timezone'], reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(StateFilter(FSMLifeCalendar.everyweek_order), F.location)
async def everyweek_order_geo(message: Message, state: FSMContext, db: SQLiteDatabase):
    time_zone = round(message.location.longitude / 15)
    db.update_time_zone(time_zone=str(time_zone), user_id=message.from_user.id)
    db.update_latitude(latitude=str(message.location.latitude), user_id=message.from_user.id)
    db.update_longitude(longitude=str(message.location.longitude), user_id=message.from_user.id)
    await state.set_state(FSMLifeCalendar.confirm_geo_process)
    await message.answer(text=f'{LEXICON_RU["everyweek_order_0"]}{time_zone}{LEXICON_RU["everyweek_order_1"]}',
                         reply_markup=yesno)
    # db.update_life_calendar(life_calendar=datetime.now().strftime('%Y-%m-%d'), id=message.from_user.id)
    # await message.answer('Включили вас в рассылку.')
    # await state.reset_state(with_data=False)


@router.message(StateFilter(FSMLifeCalendar.everyweek_order))
async def everyweek_order_repeat_no(message: Message, state: FSMContext, db: SQLiteDatabase):
    if message.text.lower().strip() == 'да':
        db.update_life_calendar(life_calendar=datetime.now().strftime('%Y-%m-%d'), user_id=message.from_user.id)
        await message.answer(text=LEXICON_RU['everyweek_order_2'], reply_markup=ReplyKeyboardRemove())
    else:
        db.update_life_calendar(life_calendar=None, user_id=message.from_user.id)
        await message.answer(text=LEXICON_RU['everyweek_order_3'], reply_markup=ReplyKeyboardRemove())
    await state.clear()
