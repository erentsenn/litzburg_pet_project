from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from tools import *



class UserData:
    user_data_menu_1 = CallbackData('to_bet')
    user_data_menu_2 = CallbackData('to_duel')
    user_data_menu_4 = CallbackData('help')

    user_data_to_bet_1 = CallbackData('iwtb', 'm_id', 'player')


class AdminData:
    cb_data_menu_1 = CallbackData('to_mailing')
    cb_data_menu_2 = CallbackData('to_add_match')
    cb_data_menu_3 = CallbackData('to_get_winners_list')

    cb_data_match_choosen = CallbackData('get_match', 'match_id')

    cb_data_winner_choose_1 = CallbackData('choose_match', 'm_id')


async def admin_menu_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text='Сделать рассылку матча',
                                       callback_data=AdminData.cb_data_menu_1.new()))
    markup.insert(InlineKeyboardButton(text='Добавить матч',
                                       callback_data=AdminData.cb_data_menu_2.new()))
    markup.insert(InlineKeyboardButton(text='Указать победителя',
                                       callback_data=AdminData.cb_data_menu_3.new()))
    return markup


async def get_matches_admin_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    for match in get_matches_sqlite():
        markup.insert(InlineKeyboardButton(text='-'.join([match[1], match[2]]),
                                            callback_data=AdminData.cb_data_match_choosen.new(match_id=match[0])))
    return markup


async def get_matches_for_winner_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    for match in get_matches_sqlite():
        markup.insert(InlineKeyboardButton(text='-'.join([match[1], match[2]]),
                                            callback_data=AdminData.cb_data_winner_choose_1.new(m_id=match[0])))
    return markup


async def user_menu_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text='Сделать ставку!',
                                       callback_data=UserData.user_data_menu_1.new()))
    markup.insert(InlineKeyboardButton(text='Запросить дуэль',
                                       callback_data=UserData.user_data_menu_2.new()))
    markup.insert(InlineKeyboardButton(text='Как заключить пари и получить выигрыш?',
                                       callback_data=UserData.user_data_menu_4.new()))
    return markup


    