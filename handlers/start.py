import logging
from aiogram import types
from aiogram.types import CallbackQuery
from db.commands import user_scenes, add_scene
from aiogram.exceptions import TelegramBadRequest
from .buttons import make_text, send_message_with_media

logger = logging.getLogger(__name__)


async def cmd_start(message: types.Message):
    try:
        scene = (await user_scenes(user_id=message.chat.id))[-1]
        await message.answer(text='Рады приветствовать! ❤️‍🔥', reply_markup=await markup(scene_=scene))
        await message.delete()
    except Exception as e:
        logger.error(f'Ошибка команды /start: {e}')


async def markup(scene_: int):
    try:
        if scene_ == 1:
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='Начать', callback_data='restart')]
            ])
        else:
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='Начать сначала', callback_data='restart')],
                [types.InlineKeyboardButton(text='Продолжить', callback_data='continue')]

            ])
        return keyboard
    except Exception as e:
        logger.error(f'Ошибка /markup: {e}')


async def restart_callback(call: CallbackQuery):
    try:
        await add_scene(user_id=call.message.chat.id, scene_=1)
        text = await make_text(user_id_=call.message.chat.id)
        await send_message_with_media(chat_id=call.message.chat.id, text=text,
                                              message_id=call.message.message_id)
        try:
            await call.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except TelegramBadRequest:
            pass
    except Exception as e:
        logger.error(f'Ошибка /restart_callback: {e}')


async def continue_callback(call: CallbackQuery):
    try:
        text = await make_text(user_id_=call.message.chat.id)
        await send_message_with_media(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id)
        try:
            await call.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except TelegramBadRequest:
            pass
    except Exception as e:
        logger.error(f'Ошибка /continue_callback: {e}')
