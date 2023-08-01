import aiogram

import os
import django

from settings import (
    BOT_PARSER_TOKEN
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from interface.backend import BackendInterface
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils import exceptions, executor

from aiogram.contrib.fsm_storage.redis import RedisStorage2


async def signal_right_cb(cb: CallbackQuery):
    bi = BackendInterface()
    data_splited = cb.data.split('_')
    id_signal = data_splited[1]
    if data_splited[2] == 'correct':
        is_correct = True
    else:
        is_correct = False
    await bi.update_signal_status(id_signal, is_correct)
    await cb.bot.answer_callback_query(cb.id, f'The Signal marked as {data_splited[2]}', show_alert=False)


bot = aiogram.Bot(token=BOT_PARSER_TOKEN)

dp = aiogram.Dispatcher(bot=bot, storage=RedisStorage2())
dp.register_callback_query_handler(signal_right_cb, lambda c: c.data.find('signal_') == 0, state='*')
aiogram.executor.start_polling(dp)
