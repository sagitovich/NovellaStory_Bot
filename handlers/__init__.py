from aiogram.filters import Command
from .start import cmd_start, restart_callback, continue_callback
from .buttons import next_button_click_callback, back_button_click_callback, variable_click_callback


def register_commands(dp):
    dp.message.register(cmd_start, Command(commands=['start']))
    dp.callback_query.register(back_button_click_callback, lambda c: c.data == 'back')
    dp.callback_query.register(next_button_click_callback, lambda c: c.data == 'next')
    dp.callback_query.register(variable_click_callback, lambda c: c.data.startswith('var'))
    dp.callback_query.register(restart_callback, lambda c: c.data == 'restart')
    dp.callback_query.register(continue_callback, lambda c: c.data.startswith('continue'))
