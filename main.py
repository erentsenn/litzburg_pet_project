import asyncio
from aiogram.bot import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import Message, CallbackQuery
from filters import AdminFilter, ApproveFilter
from configparser import ConfigParser


from keyboards import *
from tools import *
import app_logger

logger = app_logger.get_logger(__name__)

config = ConfigParser()
config.read('credentials/config.ini')
API_TOKEN = config['data']['token']
group_id = int(config['data']['group'])

bot = Bot(token=API_TOKEN)
storage = RedisStorage2('localhost', 6379, db=5, pool_size=10, prefix='arm')
loop = asyncio.get_event_loop()
dp = Dispatcher(bot=bot, storage=storage, loop=loop)
dp.filters_factory.bind(AdminFilter)
dp.filters_factory.bind(ApproveFilter)


async def on_shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()
    cur.close()
    conn.close()


class AdminStates(StatesGroup):
    menu = State()
    admin_match = State()
    admin_insert = State()
    admin_winner_match = State()
    admin_winner_player = State()


class UserStates(StatesGroup):
    menu = State()

    to_bet_1 = State()
    to_bet_2 = State()


@dp.message_handler(commands=['start'], state='*', admin=True)
async def admin_menu_start(message: Message, state: FSMContext):
    print(message.chat.id)
    await message.reply(text = 'Выберите нужную функцию', reply_markup= await admin_menu_markup())
    await AdminStates.menu.set()


#-----------------------------------------------------------------------------mailing
#-----------------------------------------------------------------------------mailing
#-----------------------------------------------------------------------------mailing

@dp.callback_query_handler(AdminData.cb_data_menu_1.filter(), state=AdminStates.menu)
async def admin_mailing_all_1(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Выберите матч', reply_markup=await get_matches_admin_markup())
    await AdminStates.admin_match.set()
    await call.answer()


@dp.callback_query_handler(AdminData.cb_data_match_choosen.filter(), state=AdminStates.admin_match)
async def admin_mailing_all_2(call: CallbackQuery, state: FSMContext, callback_data: dict):
    txt = get_match_to_bot(callback_data.get('match_id'))
    for user in get_users():
        await bot.send_message(user, f'Привет, хочу сообщить новом матче! Скорее заряжай ставку в 22 кабинете! {txt}')
    call.message.reply('Рассылка успешно выполнена!')
    await state.finish()
    await call.answer()



#-----------------------------------------------------------------------------insert match
#-----------------------------------------------------------------------------insert match
#-----------------------------------------------------------------------------insert match

@dp.callback_query_handler(AdminData.cb_data_menu_2.filter(), state=AdminStates.menu)
async def insert_match_1(call: CallbackQuery, state: FSMContext):
    await call.message.reply("""Введите имя первого соперника, второго соперника, описание в формате(Если без стадии то 0): \n Имя1 ; Имя2 ; СтадияТурнира ; Описание""")
    await AdminStates.admin_insert.set()
    await call.answer()


@dp.message_handler(state=AdminStates.admin_insert)
async def insert_match_2(message: Message, state: FSMContext):
    try:
        row = message.text.split(';')
        insert_match(row[0], row[1], row[2], row[3])
        await message.reply('Матч Успешно добавлен')
        await state.finish()
    except Exception as e:
        logger.warning(f'an error occured {e}')
        await message.reply('Случилась ошибка')
        await state.finish()


#-----------------------------------------------------------------------------------------winner
#-----------------------------------------------------------------------------------------winner
#-----------------------------------------------------------------------------------------winner
@dp.callback_query_handler(AdminData.cb_data_menu_3.filter(), state=AdminStates.menu)
async def admin_winner_1(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Выберите матч', reply_markup=await get_matches_for_winner_markup())
    await AdminStates.admin_winner_match.set()
    await call.answer()


@dp.callback_query_handler(AdminData.cb_data_winner_choose_1.filter(), state=AdminStates.admin_winner_match)
async def admin_winner_2(call: CallbackQuery, state: FSMContext, callback_data: dict):
    m_id = callback_data.get('m_id')
    await state.update_data(admin_winner_match=m_id)
    await call.message.reply('Введите имя победителя:')
    await AdminStates.admin_winner_player.set()
    await call.answer()


@dp.message_handler(state=AdminStates.admin_winner_player)
async def admin_winner_3(message: Message, state: FSMContext):
    async with state.proxy() as data:
        m_id = data.get('admin_winner_match')
    players_blya = get_winners(m_id)
    f = False
    for p in players_blya:
        if p.lstrip().rstrip() == message.text:
            f = True
    if not f:
        await message.reply(f'Ой, кажется нет таких игроков в матче {m_id}')
    else:
        try:
            change_winner(m_id, message.text)
            bet_winners, shared_prize = get_winners_bet(m_id, message.text)

            shared_lose = get_sum_lose(m_id, message.text)
            for w in bet_winners:
                text = f"{players_blya[0]} - {players_blya[1]} | {w[2]}, поставил {w[3]} "
                try:
                    prize = (w[3] + ((w[3] * shared_lose) / shared_prize) * 0.70) - (w[3] + ((w[3] * shared_lose) / shared_prize) * 0.70) % 5
                    text += f'Выиграл {prize}'
                    await bot.send_message(chat_id=w[1], text=f'Вы верно угадали пари! Приходите в 22 кабинет за заслуженной наградой в {prize} лицов')
                except Exception as e:
                    await message.reply(f'shit happened need to hand-work {w}')
                await bot.send_message(chat_id=-847941951, text=text)
            await state.finish()
        except Exception as e:
            await message.reply('shit happened need to hand-work')
            print(e)

#-----------------------------------------------------------------------------------------approve_handler
#-----------------------------------------------------------------------------------------approve_handler
#-----------------------------------------------------------------------------------------approve handler
@dp.message_handler(commands=['break'], state='*')
async def break_fsm(message: Message, state: FSMContext):
    await state.finish()
    await message.reply('Мы выбрались отсюда!')





@dp.message_handler(approve=True, state='*')
async def get_update_in_chat(message: Message):
    flag, row = if_in_bets(message.text)
    if flag:
        await message.reply(f'id = {row[0]}, на {row[1]}, пользователь {row[2]} поставил {row[3]} Approvement!')
    else:
        await message.reply(f'An error occured need hand-work')


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""#user
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""#user
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""#user

#-----------------------------------------------------------------------------------------to_bet
#-----------------------------------------------------------------------------------------to_bet
#-----------------------------------------------------------------------------------------to_bet
@dp.callback_query_handler(UserData.user_data_menu_1.filter(), admin=False, state=UserStates.menu)
async def to_bet_user_1(call: CallbackQuery, state: FSMContext):
    await call.message.reply('Отлично! Просмотрите доступные матчи:')
    for m_id, row in get_matches_with_players_for_user().items():
        markup = InlineKeyboardMarkup(row_width=2)
        markup.insert(InlineKeyboardButton(text=row[0],
                                            callback_data=UserData.user_data_to_bet_1.new(m_id=m_id, player=row[0])))
        markup.insert(InlineKeyboardButton(text=row[1],
                                            callback_data=UserData.user_data_to_bet_1.new(m_id=m_id, player=row[1])))
        await bot.send_message(call.message.chat.id, row[2], reply_markup=markup)
    await UserStates.to_bet_1.set()


@dp.callback_query_handler(UserData.user_data_to_bet_1.filter(), state=UserStates.to_bet_1, admin=False)
async def to_bet_user_2(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await UserStates.to_bet_2.set()
    m_id = callback_data.get('m_id')
    player = callback_data.get('player')
    await state.update_data(to_bet_user_1=m_id)
    await state.update_data(to_bet_user_2=player)
    await call.message.reply('Теперь введите сумму ставки, она должна быть хотя бы 25')


@dp.message_handler(state=UserStates.to_bet_2)
async def to_bet_user_3(message: Message, state: FSMContext):
    try:
        if int(message.text) >= 25 and int(message.text) <= 10000:         
            async with state.proxy() as data:
                m_id = data.get('to_bet_user_1')
                player = data.get('to_bet_user_2')
            bet = int(message.text)
            code = insert_bet(m_id, player, message.chat.id, message.from_user.username, bet)
            await message.reply(f'Отлично, ваша ставка есть в нашей базе, осталось сдать деньги крупье и сообщить ему код: {code}, иначе ставка не будет засчитана')
            await state.finish()
        else:
            await message.reply('Кажется вы ввели слишком маленькую или слишком большую сумму')
    except Exception as e:
        await message.reply('Кажется ввод некорректен, попробуйте еще раз')
        print(e)
    

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""#user
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""#user
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""#user

@dp.message_handler(admin=False, state='*')
async def user_start(message: Message, state: FSMContext):
    print(message.chat.id)
    await message.reply("Привет! Я - Бот 11 физмата, который поможет тебе заключить пари на турнире по армрестлингу. Выбери функцию, которая тебя интересует:", 
    reply_markup=await user_menu_markup())
    await UserStates.menu.set()
    insert_user(message.chat.id, message.from_user.username)


#-----------------------------------------------------------------------------------------to_duel-897721218
#-----------------------------------------------------------------------------------------to_duel-897721218
#-----------------------------------------------------------------------------------------to_duel-897721218



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)

