import asyncio
import datetime
from telethon import TelegramClient, sync, events, hints


from telethon import events
from telethon.tl.patched import Message



from parserTelethone.keyboards.keyboards import KeyboardManager
from parserTelethone.utils.Parser import Parser
from parserTelethone.utils.check_folder import is_in_folder
from parserTelethone.utils.text_message import create_message


class SignalsParser:
    def __init__(self, bot, api_id, api_hash, bi, log, proxy=None, session_name='session_name', ):
        self.client = TelegramClient(session_name, api_id, api_hash, proxy=proxy)
        self.bot = bot
        self.log = log
        # handler for messages
        self.client.add_event_handler(self.new_message_cb, events.NewMessage())
        self.bi = bi



    async def new_message_cb(self, event: Message):
        input_id = event.chat_id
        message_text = event.message.text.replace('*', '')
        try:
            channel_name = event.chat.title
        except Exception as err:
            self.log.exception(err)
        if event.is_channel is True:
            input_id = event.input_chat.channel_id
        chat_folder = await is_in_folder(event.client, input_id, ('Индюки сигна', 'Сигналы фьюч'))
        if not chat_folder:
            return
        message_parser = Parser(self.log)
        parsed_dct = await message_parser.parse_message(event.message.text)
        if parsed_dct.get('pair') and parsed_dct.get('type'):
            now_time = datetime.datetime.now(tz=datetime.timezone.utc)
            self.log.info(f"{now_time} = {event.chat} = {parsed_dct.get('pair')} = {parsed_dct.get('timeframe')} ")
            # берем последний похожий сигнал
            tf_data = parsed_dct.get('timeframe') if parsed_dct.get('timeframe') else None
            last_signals = await self.bi.get_signals(time_frame=tf_data,
                                                     currency_pair=parsed_dct.get('pair').upper(),
                                                     type=parsed_dct.get('type'), datet=now_time)
            features_pass = True if chat_folder == 'Сигналы фьюч' else False

            if features_pass or len(last_signals) >= 2:
                # Если подобных сигналов больше 3. Указываем 2, потому что новый сигнал не учитывается
                self.log.info(f"{now_time} = {event.chat} = {parsed_dct.get('pair')} = {parsed_dct.get('timeframe')} ")
                # Запушили сигнал в базу для итоговых сигналов
                signal = await self.bi.add_compared_signal(
                    time_frame=parsed_dct.get('timeframe'),
                    currency_pair=parsed_dct.get('pair').upper(),
                    type=parsed_dct.get('type'),
                    leverage=parsed_dct.get('leverage'),
                    entry_target=parsed_dct.get('entry_targets'),
                    take_profit=parsed_dct.get('take_profit'),
                    stop=parsed_dct.get('stop'),
                    title=channel_name
                )

                # отправка сообщения в каналы
                keyboard = KeyboardManager.signal_correct(signal.id)
                # todo in env
                await self.bot.send_message(6185258473, create_message(parsed_dct), reply_markup=keyboard)
                print('SENDED\n\n')
            # добавляем ко всем сигналам
            await self.bi.add_signal(
                time_frame=parsed_dct.get('timeframe'),
                currency_pair=parsed_dct.get('pair').upper(),
                type=parsed_dct.get('type'),
                leverage=parsed_dct.get('leverage'),
                entry_target=parsed_dct.get('entry_targets'),
                take_profit=parsed_dct.get('take_profit'),
                stop=parsed_dct.get('stop'),
                title=channel_name
            )

    async def start(self):
        await self.client.start()
        await self.client.run_until_disconnected()
        await self.client.disconnect()
