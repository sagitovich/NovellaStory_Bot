import os
import json
import logging
import bot_init
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile
from db.commands import user_scenes, add_scene, pop_scene, user_media, add_media

logger = logging.getLogger(__name__)
with open('/var/www/html/novells/BattyAndGrant/story/story.json', 'r', encoding='utf-8') as f:
    novel_data = json.load(f)


async def keyboard_markup(user_id_):
    try:
        all_user_scenes = await user_scenes(user_id=user_id_)
        data = novel_data[str(all_user_scenes[-1])]
        if len(data["buttons"]) > 1:
            buttons = [
                [types.InlineKeyboardButton(text=button["text"], callback_data=f"var{index + 1}")]
                for index, button in enumerate(data["buttons"])
            ]
            buttons.append([types.InlineKeyboardButton(text='⬅️', callback_data='back')])
            markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        elif not data['auto_step']:
            markup = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='⬅️', callback_data='back')]
            ])
        elif len(all_user_scenes) == 1:
            markup = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='➡️', callback_data='next')]
            ])
        else:
            markup = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='⬅️', callback_data='back'),
                 types.InlineKeyboardButton(text='➡️', callback_data='next')]
            ])
        return markup
    except Exception as e:
        logger.error(f'Ошибка /keyboard_markup: {e}')


async def back_step(user_id_):
    try:
        all_user_scenes = await user_scenes(user_id=user_id_)
        if len(all_user_scenes) > 1:
            await pop_scene(user_id=user_id_)
    except Exception as e:
        logger.error(f'Ошибка /back_step: {e}')


async def next_step(user_id_):
    try:
        current_scene = (await user_scenes(user_id=user_id_))[-1]
        data = novel_data[str(current_scene)]
        await add_scene(user_id=user_id_, scene_=data['auto_step'])
    except Exception as e:
        logger.error(f'Ошибка /next_step: {e}')


async def make_text(user_id_):
    try:
        current_scene = (await user_scenes(user_id=user_id_))[-1]
        data = novel_data[str(current_scene)]
        character_name = data['name']
        if not character_name:
            character_name = ''
        character_text = data['text']
        return f'<b>{character_name}</b>\n{character_text}'
    except Exception as e:
        logger.error(f'Ошибка /make_text: {e}')


async def send_message_with_media(chat_id, text, message_id):
    try:
        current_scene = (await user_scenes(user_id=chat_id))[-1]
        previous_media = await user_media(user_id=chat_id)
        data = novel_data[str(current_scene)]
        media_files = data.get('media', [])
        if media_files:
            for file in media_files:
                file_path = os.path.join('/var/www/html/novells/BattyAndGrant/story/photos', file)
                if len(previous_media) == 0 or previous_media[-1] == '-':
                    await add_media(user_id=chat_id, file=file_path)
                    photo = FSInputFile(file_path)
                    await bot_init.bot.send_photo(chat_id=chat_id, photo=photo, caption=text,
                                                  parse_mode=ParseMode.HTML, reply_markup=await keyboard_markup(chat_id))
                    await bot_init.bot.delete_message(chat_id=chat_id, message_id=message_id)
                elif file_path != previous_media[-1]:
                    await add_media(user_id=chat_id, file=file_path)
                    photo = FSInputFile(file_path)
                    await bot_init.bot.send_photo(chat_id=chat_id, photo=photo, caption=text,
                                                  parse_mode=ParseMode.HTML, reply_markup=await keyboard_markup(chat_id))
                    await bot_init.bot.delete_message(chat_id=chat_id, message_id=message_id)
                else:
                    try:
                        await bot_init.bot.edit_message_caption(chat_id=chat_id, message_id=message_id,
                                                                caption=text, parse_mode=ParseMode.HTML,
                                                                reply_markup=await keyboard_markup(chat_id))
                    except TelegramBadRequest:
                        await add_media(user_id=chat_id, file=file_path)
                        photo = FSInputFile(file_path)
                        await bot_init.bot.send_photo(chat_id=chat_id, photo=photo, caption=text,
                                                      parse_mode=ParseMode.HTML, reply_markup=await keyboard_markup(chat_id))
        else:
            await bot_init.bot.send_message(chat_id=chat_id, text=text,
                                            parse_mode=ParseMode.HTML, reply_markup=await keyboard_markup(chat_id))
            if len(previous_media) != 0:
                await bot_init.bot.delete_message(chat_id=chat_id, message_id=message_id)
            await add_media(user_id=chat_id, file='')
    except Exception as e:
        logger.error(f'Ошибка /send_message_with_media: {e}')


async def back_button_click_callback(call: CallbackQuery):
    try:
        await back_step(user_id_=call.message.chat.id)
        text = await make_text(user_id_=call.message.chat.id)
        await send_message_with_media(chat_id=call.message.chat.id, text=text,
                                      message_id=call.message.message_id)
    except Exception as e:
        logger.error(f'Ошибка /back_btn: {e}')


async def next_button_click_callback(call: CallbackQuery):
    try:
        await next_step(user_id_=call.message.chat.id)
        text = await make_text(user_id_=call.message.chat.id)
        await send_message_with_media(chat_id=call.message.chat.id, text=text,
                                      message_id=call.message.message_id)
    except Exception as e:
        logger.error(f'Ошибка /next_btn: {e}')


async def variable_click_callback(call: CallbackQuery):  # кнопки выбора сюжетной ветки
    try:
        current_scene = (await user_scenes(user_id=call.message.chat.id))[-1]
        data = novel_data[str(current_scene)]
        for index, button in enumerate(data["buttons"]):
            if call.data == f"var{index+1}":
                await add_scene(user_id=call.message.chat.id, scene_=button["to_step"])
                text = await make_text(user_id_=call.message.chat.id)
                await send_message_with_media(chat_id=call.message.chat.id, text=text,
                                              message_id=call.message.message_id)
                break
    except Exception as e:
        logger.error(f'Ошибка /var_click: {e}')
